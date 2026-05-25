from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

from src.core.models import Chunk, RetrievedChunk
from src.rag.retrieval.hybrid import HybridRetriever, _reciprocal_rank_fusion


def _chunk(content: str = "test") -> Chunk:
    return Chunk(id=uuid.uuid4(), document_id=uuid.uuid4(), content=content)


def test_rrf_empty_lists() -> None:
    assert _reciprocal_rank_fusion([], []) == []


def test_rrf_overlap_scores_higher() -> None:
    c1, c2, c3 = _chunk(), _chunk(), _chunk()
    result = _reciprocal_rank_fusion([c1, c2], [c2, c3])
    # c2 appears in both → highest combined score
    assert result[0].chunk.id == c2.id


def test_rrf_no_overlap_returns_all() -> None:
    c1, c2 = _chunk(), _chunk()
    result = _reciprocal_rank_fusion([c1], [c2])
    assert len(result) == 2


def test_rrf_uses_hybrid_method_label() -> None:
    c = _chunk()
    result = _reciprocal_rank_fusion([c], [])
    assert result[0].retrieval_method == "hybrid_rrf"


async def test_hybrid_retrieve_calls_both() -> None:
    vector = AsyncMock()
    bm25 = MagicMock()
    chunks = [_chunk(), _chunk()]
    vector.retrieve.return_value = chunks
    bm25.retrieve.return_value = chunks

    retriever = HybridRetriever(vector, bm25)
    results = await retriever.retrieve("query", top_k=2)

    vector.retrieve.assert_called_once()
    bm25.retrieve.assert_called_once()
    assert len(results) <= 2
    assert all(isinstance(r, RetrievedChunk) for r in results)


async def test_hybrid_retrieve_empty_sources() -> None:
    vector = AsyncMock()
    bm25 = MagicMock()
    vector.retrieve.return_value = []
    bm25.retrieve.return_value = []

    retriever = HybridRetriever(vector, bm25)
    assert await retriever.retrieve("query") == []


async def test_hybrid_retrieve_requests_2x_top_k() -> None:
    vector = AsyncMock()
    bm25 = MagicMock()
    vector.retrieve.return_value = []
    bm25.retrieve.return_value = []

    retriever = HybridRetriever(vector, bm25)
    await retriever.retrieve("q", top_k=5)

    vector.retrieve.assert_called_once_with("q", top_k=10)
    bm25.retrieve.assert_called_once_with("q", top_k=10)
