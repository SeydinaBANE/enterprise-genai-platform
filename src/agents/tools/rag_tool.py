from __future__ import annotations

from langchain_core.tools import tool

from src.observability.logging import get_logger

logger = get_logger(__name__)

_retriever = None


def set_retriever(retriever: object) -> None:
    global _retriever
    _retriever = retriever


@tool
async def rag_query(question: str) -> str:
    """Query the knowledge base using RAG. Use for questions about indexed documents."""
    if _retriever is None:
        return "Knowledge base not available."

    from src.rag.retrieval.hybrid import HybridRetriever

    if not isinstance(_retriever, HybridRetriever):
        return "Retriever not properly configured."

    results = await _retriever.retrieve(question, top_k=5)
    if not results:
        return "No relevant information found."

    parts = [f"[{i + 1}] {r.chunk.content}" for i, r in enumerate(results)]
    return "\n\n".join(parts)
