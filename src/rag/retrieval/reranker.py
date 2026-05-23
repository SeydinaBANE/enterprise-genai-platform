from __future__ import annotations

from src.core.models import RetrievedChunk
from src.observability.logging import get_logger

logger = get_logger(__name__)


async def rerank(
    query: str,
    candidates: list[RetrievedChunk],
    top_k: int = 5,
) -> list[RetrievedChunk]:
    """Score-based reranker using query-chunk overlap heuristic.

    Replace with a cross-encoder model (e.g. ms-marco-MiniLM) for production.
    """
    query_tokens = set(query.lower().split())

    scored: list[tuple[float, RetrievedChunk]] = []
    for candidate in candidates:
        chunk_tokens = set(candidate.chunk.content.lower().split())
        overlap = len(query_tokens & chunk_tokens)
        combined = candidate.score + 0.1 * overlap / max(len(query_tokens), 1)
        scored.append((combined, candidate))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [rc for _, rc in scored[:top_k]]
    logger.info("reranked", input=len(candidates), output=len(results))
    return results
