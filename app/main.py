import logfire
import os
from dotenv import load_dotenv
load_dotenv()
logfire.configure(token=os.getenv("LOGFIRE_TOKEN"))

# Now safe to import app modules - logfire is already active
from fastapi import FastAPI, Response
from app.agents.graph import rag_agent, checkpointer
from pydantic import BaseModel
from typing import Optional
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.middleware.rate_limit import limiter
from app.guardrails import check_input


app=FastAPI(title="READFLIX LIBRARY RAG API")
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler,
)
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)
templates = Jinja2Templates(
    directory="app/templates"
)

class QueryRequest(BaseModel):
    q:str
    thread_id: Optional[str] = "default_user"
    
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.exception_handler(404)
async def not_found(request: Request, exc):
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        status_code=404,
        context={},
    )
    
@app.post("/query")
@limiter.limit("20/minute")
async def query(request: Request, data: QueryRequest):
    q = data.q
    thread_id = data.thread_id

    guard = await check_input(q)

    if guard["action"] != "allow":
        return {
            "question": q,
            "answer": guard["message"],
            "status": guard["action"],
        }

    initial_state = {
        "messages": [{"role": "user", "content": q}],
        "current_query": q,
        "documents": [],
        "plan": ["Start"],
        "status": "Initializing Graph...",
    }

    config = {"configurable": {"thread_id": thread_id}}

    try:
        final_output = await rag_agent.ainvoke(
            initial_state,
            config=config,
        )

        return {
            "question": q,
            "answer": final_output.get("answer", ""),
            "status": final_output.get("status", "completed"),
        }

    except Exception:
        logfire.exception("❌ RAG execution failed")
        return {
            "question": q,
            "answer": "I’m not able to answer that right now. Please try again in a moment.",
            "status": "error",
        }
        
@app.delete("/thread/{thread_id}")
async def delete_thread(thread_id: str):
    try:
        await checkpointer.adelete_thread(thread_id)
        logfire.info(
            "🗑️ Thread deleted",
            thread_id=thread_id,
        )

        return {
            "status": "deleted"
        }

    except Exception:
        logfire.exception("❌ Thread deletion failed")

        return {
            "status": "error"
        }