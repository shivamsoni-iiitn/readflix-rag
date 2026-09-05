import os
import time

import boto3
import logfire
from flashrank import Ranker, RerankRequest


BUCKET = os.environ["MODEL_BUCKET"]
S3_PREFIX = "flashrank/ms-marco-TinyBERT-L-2-v2/"
LOCAL_DIR = "/app/models/flashrank"
MODEL_NAME = "ms-marco-TinyBERT-L-2-v2"


_ranker = None


def download_flashrank_model():
    model_dir = os.path.join(LOCAL_DIR, MODEL_NAME)

    if os.path.exists(model_dir):
        logfire.info("FlashRank model already exists locally")
        return

    os.makedirs(LOCAL_DIR, exist_ok=True)

    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")

    logfire.info("Downloading FlashRank model from S3...")

    for page in paginator.paginate(Bucket=BUCKET, Prefix=S3_PREFIX):
        for obj in page.get("Contents", []):
            key = obj["Key"]

            if key.endswith("/"):
                continue

            relative_path = key[len(S3_PREFIX):]
            destination = os.path.join(LOCAL_DIR, relative_path)

            os.makedirs(os.path.dirname(destination), exist_ok=True)
            s3.download_file(BUCKET, key, destination)

    logfire.info("FlashRank model downloaded from S3")


def _get_ranker() -> Ranker:
    global _ranker

    if _ranker is None:
        logfire.info("Initializing FlashRank Model locally...")

        _ranker = Ranker(
            model_name=MODEL_NAME,
            cache_dir=LOCAL_DIR,
        )

    return _ranker


def rerank_documents(
    query: str,
    documents: list[str],
    top_n: int = 5,
) -> list[str]:

    if not documents:
        return []

    start_time = time.time()

    logfire.info(
        f"[Reranker] Sending {len(documents)} docs to FlashRank Cross-Encoder..."
    )

    try:
        ranker = _get_ranker()

        passages = [
            {"id": i, "text": doc}
            for i, doc in enumerate(documents)
        ]

        request = RerankRequest(
            query=query,
            passages=passages,
        )

        results = ranker.rerank(request)

        reranked_docs = [
            result["text"]
            for result in results[:top_n]
        ]

        duration = time.time() - start_time
        top_score = results[0]["score"] if results else "N/A"

        logfire.info(
            f"[Reranker] Done in {duration:.2f}s. "
            f"Top semantic score: {top_score}"
        )

        return reranked_docs

    except Exception as e:
        logfire.error(f"[Reranker] Semantic Reranking failed: {e}")
        return documents[:top_n]


# import time
# import logfire
# from flashrank import Ranker, RerankRequest

# _ranker=None

# def _get_ranker() -> Ranker:
#     """
#     Initializes the flashrank engine lazily.
#     Flashrank uses a local ONNX model (ms-macro-MiniLM-L-6-v2) for ultra-fast reranking.
#     """
#     global _ranker
#     if _ranker is None:
#         logfire.info("Ininitalizing FlashRank Model (TinyBERT) locally...")
#         try:
#             _ranker=Ranker(cache_dir="/tmp/flashrank")
#         except Exception:
#             _ranker=Ranker()
#     return _ranker

# def rerank_documents(query: str, documents: list[str], top_n: int=5)-> list[str]:
#     """
#     Refines retrieval results by re-scoring documents against the query semantically.
    
#     Why FlashRank? 
#     Standard vector search (Cosine Similarity) is fast but mathematically "fuzzy."
#     FlashRank uses a Cross-Encoder approach which is much more precise but usually slow.
#     FlashRank solves this by using highly optimized, quantized ONNX models locally.
#     """
#     if not documents:
#         return []
    
#     start_time=time.time()
#     logfire.info(f"[Reranker] Sending {len(documents)} docs to FlashRank Cross-Encoder...")
    
#     try:
#         ranker = _get_ranker()
#         passages=[
#             {"id":i, "text": doc}
#             for i,doc in enumerate(documents)
#         ]
        
#         request=RerankRequest(query=query, passages=passages)
#         results=ranker.rerank(request)
#         reranked_docs=[]
#         for res in results[:top_n]:
#             reranked_docs.append(res['text'])
        
#         duration=time.time() - start_time
#         top_score= results[0]['score'] if results else 'N/A'
#         logfire.info(f"[Reranker] Done in {duration:.2f}s. Top semantic score: {top_score}")
        
#         return reranked_docs
    
#     except Exception as e:
#         logfire.error(f"[Reranker] Semantic Reranking failed:{e}")
#         return documents[:top_n]
    
