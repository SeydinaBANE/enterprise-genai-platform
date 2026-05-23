from __future__ import annotations

from collections import defaultdict

from src.core.models import Chunk, RetrievedChunk
from src.observability.logging import get_logger
from src.rag.retrieval.bm25 import BM25Retriever
from src.rag.retrieval.vector_store import ChromaRetriever

logger = get_logger(__name__)

RRF_K = 60


def _reciprocal_rank_fusion(
    semantic: list[Chunk],
    keyword: list[Chunk],
    k: int = RRF_K,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = defaultdict(float)
    chunks_by_id: dict[str, Chunk] = {}

    for rank, chunk in enumerate(semantic):
        cid = str(chunk.id)
        scores[cid] += 1.0 / (k + rank + 1)
        chunks_by_id[cid] = chunk

    for rank, chunk in enumerate(keyword):
        cid = str(chunk.id)
        scores[cid] += 1.0 / (k + rank + 1)
        chunks_by_id[cid] = chunk

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        RetrievedChunk(chunk=chunks_by_id[cid], score=score, retrieval_method="hybrid_rrf")
        for cid, score in ranked
    ]


class HybridRetriever:
    def __init__(self, vector_store: ChromaRetriever, bm25: BM25Retriever) -> None:
        self._vector = vector_store
        self._bm25 = bm25

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        semantic = await self._vector.retrieve(query, top_k=top_k * 2)
        keyword = self._bm25.retrieve(query, top_k=top_k * 2)

        fused = _reciprocal_rank_fusion(semantic, keyword)
        results = fused[:top_k]
        logger.info(
            "hybrid_retrieve",
            semantic=len(semantic),
            keyword=len(keyword),
            fused=len(results),
        )
        return results
