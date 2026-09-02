import time
import logfire
from flashrank import Ranker, RerankRequest

_ranker=None

def _get_ranker() -> Ranker:
    """
    Initializes the flashrank engine lazily.
    Flashrank uses a local ONNX model (ms-macro-MiniLM-L-6-v2) for ultra-fast reranking.
    """
    global _ranker
    if _ranker is None:
        logfire.info("Ininitalizing FlashRank Model (TinyBERT) locally...")
        try:
            _ranker=Ranker(cache_dir="/tmp/flashrank")
        except Exception:
            _ranker=Ranker()
    return _ranker

def rerank_documents(query: str, documents: list[str], top_n: int=5)-> list[str]:
    """
    Refines retrieval results by re-scoring documents against the query semantically.
    
    Why FlashRank? 
    Standard vector search (Cosine Similarity) is fast but mathematically "fuzzy."
    FlashRank uses a Cross-Encoder approach which is much more precise but usually slow.
    FlashRank solves this by using highly optimized, quantized ONNX models locally.
    """
    if not documents:
        return []
    
    start_time=time.time()
    logfire.info(f"[Reranker] Sending {len(documents)} docs to FlashRank Cross-Encoder...")
    
    try:
        ranker = _get_ranker()
        passages=[
            {"id":i, "text": doc}
            for i,doc in enumerate(documents)
        ]
        
        request=RerankRequest(query=query, passages=passages)
        results=ranker.rerank(request)
        reranked_docs=[]
        for res in results[:top_n]:
            reranked_docs.append(res['text'])
        
        duration=time.time() - start_time
        top_score= results[0]['score'] if results else 'N/A'
        logfire.info(f"[Reranker] Done in {duration:.2f}s. Top semantic score: {top_score}")
        
        return reranked_docs
    
    except Exception as e:
        logfire.error(f"[Reranker] Semantic Reranking failed:{e}")
        return documents[:top_n]
    