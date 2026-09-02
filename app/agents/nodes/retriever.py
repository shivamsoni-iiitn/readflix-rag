from app.agents.state import AgentState
from app.config import settings
import logfire
from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.ranking_service import rerank_documents
from guardrails import Guard
from app.guardrails.validators import ReadflixContextInjection


context_guard = Guard().use(ReadflixContextInjection(on_fail="exception"))

def retrieve_node(state: AgentState):
    """
    Performs vector search and semantic reranking for technical queries.
    """
    query=state["current_query"]
    
    #Standard retrieval 
    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")
        raw_results = search_enterprise_knowledge(query, limit=15)
        logfire.info(f"Retrieved {len(raw_results)} candidates from Vector DB")
    
        doc_content=[doc['content'] for doc in raw_results]
        
        with logfire.span("⚖️ Semantic Reranking"):
            reranked_contents = rerank_documents(query, doc_content, top_n=5)
            logfire.info("Reranking complete. Kept top 5 most relevant chunks.")
        
        
        safe_docs = []

        for doc in reranked_contents:
            try:
                context_guard.validate(doc)
                safe_docs.append(doc)
            except Exception:
                logfire.warning("🚫 Poisoned context chunk removed")

        formatted_docs = [f"CONTENT: {doc}" for doc in safe_docs]
            
    return {
        "documents": formatted_docs,
        "status": f"Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"]
    }