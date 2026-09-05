from app.agents.state import AgentState
import logfire

from app.services.retrieval.qdrant_service import search_enterprise_knowledge
from app.services.retrieval.ranking_service import rerank_documents


def retrieve_node(state: AgentState):
    """
    Performs vector search and semantic reranking for technical queries.
    """
    query = state["current_query"]

    with logfire.span("🔍 Knowledge Retrieval"):
        logfire.info(f"Searching Qdrant for: {query}")

        raw_results = search_enterprise_knowledge(query, limit=5)

        logfire.info(
            f"Retrieved {len(raw_results)} candidates from Vector DB"
        )

        doc_content = [doc["content"] for doc in raw_results]

        with logfire.span("⚖️ Semantic Reranking"):
            reranked_contents = rerank_documents(
                query,
                doc_content,
                top_n=2,
            )

            logfire.info(
                "Reranking complete. Kept top 5 most relevant chunks."
            )

        formatted_docs = [
            f"CONTENT: {doc}"
            for doc in reranked_contents
        ]

    return {
        "documents": formatted_docs,
        "status": "Found technical context.",
        "plan": state["plan"] + ["Context Retrieved"],
    }