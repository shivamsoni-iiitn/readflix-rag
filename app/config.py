import os
from dotenv import load_dotenv

load_dotenv()

langchain_api_key = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY") or ""
langchain_project = os.getenv("LANGCHAIN_PROJECT") or os.getenv("LANGSMITH_PROJECT") or "rag_readflix"
langchain_endpoint = os.getenv("LANGCHAIN_ENDPOINT") or os.getenv("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com"
langchain_tracing = os.getenv("LANGCHAIN_TRACING_V2") or os.getenv("LANGSMITH_TRACING") or "true"

os.environ["LANGCHAIN_TRACING_V2"] = str(langchain_tracing).lower()
os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
os.environ["LANGCHAIN_PROJECT"] = langchain_project
os.environ["LANGCHAIN_ENDPOINT"] = langchain_endpoint

# Compatibility aliases for apps or integrations still reading LANGSMITH_*.
if langchain_api_key:
    os.environ["LANGSMITH_API_KEY"] = langchain_api_key
if langchain_project:
    os.environ["LANGSMITH_PROJECT"] = langchain_project
if langchain_endpoint:
    os.environ["LANGSMITH_ENDPOINT"] = langchain_endpoint
os.environ["LANGSMITH_TRACING"] = str(langchain_tracing).lower()


class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_URL: str = os.getenv("QDRANT_CLUSTER_ENDPOINT")
    QDRANT_COLLECTION: str = "Readflix_Library"
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = "llama-3.3-70b-versatile"
    OPENAI_MODEL = "gpt-5-nano"

    AWS_GUARDRAIL_ID: str = os.getenv("AWS_GUARDRAIL_ID")
    AWS_GUARDRAIL_VERSION: str = os.getenv("AWS_GUARDRAIL_VERSION")
    AWS_REGION: str = os.getenv("AWS_DEFAULT_REGION")

    LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2", "true")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY") or os.getenv("LANGSMITH_API_KEY") or ""
    LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT") or os.getenv("LANGSMITH_PROJECT") or "rag_readflix"
    LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT") or os.getenv("LANGSMITH_ENDPOINT") or "https://api.smith.langchain.com"
    DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")

settings = Settings()
