import asyncio
import time

import logfire
from litellm import Router

from app.config import settings


llm_router = Router(
    model_list=[
        {
            "model_name": "primary",
            "litellm_params": {
                "model": f"openai/{settings.OPENAI_MODEL}",
                "api_key": settings.OPENAI_API_KEY,
            },
        },
        {
            "model_name": "fallback",
            "litellm_params": {
                "model": f"groq/{settings.GROQ_MODEL}",
                "api_key": settings.GROQ_API_KEY,
            },
        },
    ],
    num_retries=2,
    fallbacks=[{"primary": ["fallback"]}],
)

_llm_limit = asyncio.Semaphore(5)


async def generate(messages: list[dict], feature: str = "rag"):
    start = time.perf_counter()

    logfire.info("⏳ LLM request waiting for slot", feature=feature)

    async with _llm_limit:
        with logfire.span("🤖 LLM Gateway", feature=feature):
            try:
                response = await llm_router.acompletion(
                    model="primary",
                    messages=messages,
                )

                usage = getattr(response, "usage", None)

                logfire.info(
                    "✅ LLM request completed",
                    feature=feature,
                    model=response.model,
                    latency_ms=round((time.perf_counter() - start) * 1000, 2),
                    total_tokens=getattr(usage, "total_tokens", None),
                )

                return response

            except Exception:
                logfire.exception("❌ LLM Gateway failed", feature=feature)
                
                raise