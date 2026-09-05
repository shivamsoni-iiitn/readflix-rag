import time
import logfire
from langchain_openai import OpenAIEmbeddings
from app.config import settings

BATCH_SIZE = 50
_OPENAI_DIMENSION = 1536
_FALLBACK_DIMENSION = 768  #all mpnet base v2

_active_model =None
_model_type:str | None = None

def _probe_openai():
    """Try one embedding request to OpenAI to check if the API key is valid and the service is reachable. Returns Model or None"""
    try:
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=settings.OPENAI_API_KEY
        )
        embeddings.embed_query('probe')
        logfire.info("OpenAI Embeddings Ready")
        return embeddings
    except Exception as e:
        logfire.warning(f"OpenAI probe failed: {e}, Will use fallback model")
        return None        
    
# def _load_fallback():
#     from sentence_transformers import SentenceTransformer
#     logfire.info("Loading sentence transformer fallback (all-mpnet-base-v2, 768 dim)")
#     return SentenceTransformer("all-mpnet-base-v2")

def _init():
    global _active_model,_model_type
    if _active_model is not None:
        return
    openai=_probe_openai()
    if openai:
        _active_model = openai
        _model_type="openai"
    else:
        raise RuntimeError(
            "OpenAI embedding service is unavailable. "
            "No fallback embedding model is configured."
        )
        # _active_model= _load_fallback()
        # _model_type= "fallback"
        
def get_embedding_dim() -> int:
    if _model_type is None:
        raise RuntimeError(
            "Embedding model not initialized. "
            "Call _init() before get_embedding_dim()."
        )

    if _model_type == "openai":
        return _OPENAI_DIMENSION

    return _FALLBACK_DIMENSION
    
def _embed_batch(batch: list[str])-> list[list[float]]:
    if _model_type=="openai":
        for attempt in range(4):
            try:
                return _active_model.embed_documents(batch)
            except Exception as e:
                err=str(e).lower()
                is_rate_limit=any(x in err for x in ("429", "rate","quota", "resource_exhausted"))
                if is_rate_limit and attempt<3:
                    wait=2 ** attempt
                    logfire.warning(
                        f"OpenAI rate limit hit - retrying on {wait}sec "
                        f"(attempt {attempt +1}/4)"
                    )
                    time.sleep(wait)
                else:
                    logfire.error(f"Openai embeddings failed: {e}")
                    raise
        raise RuntimeError("OpenAI rate limit persisted after 4 attemps.")
    else:    
        return _active_model.encode(batch, show_progress_bar=False).tolist()
    

def embed_query(query: str)-> list[float]:
    _init()
    if _model_type=="openai":
        return _active_model.embed_query(query)
    return _active_model.encode([query])[0].tolist()

def embed_texts(texts: list[str])-> list[list[float]]:
    _init()
    all_embeddings: list[list[float]]=[]
    for i in range(0, len(texts), BATCH_SIZE):
        batch=texts[i:i+BATCH_SIZE]
        with logfire.span("Embed batch", model=_model_type, start=i, size=len(batch)):
            all_embeddings.extend(_embed_batch(batch))
    return all_embeddings