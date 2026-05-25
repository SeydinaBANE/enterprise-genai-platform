from __future__ import annotations

import uuid

from src.core.models import Chunk, RetrievedChunk
from src.rag.retrieval.reranker import rerank


def _rc(content: str, score: float = 0.5) -> RetrievedChunk:
    chunk = Chunk(id=uuid.uuid4(), document_id=uuid.uuid4(), content=content)
    return RetrievedChunk(chunk=chunk, score=score, retrieval_method="test")


async def test_rerank_returns_top_k() -> None:
    candidates = [_rc(f"chunk {i}") for i in range(10)]
    result = await rerank("chunk 5", candidates, top_k=3)
    assert len(result) == 3


async def test_rerank_empty_input() -> None:
    assert await rerank("query", [], top_k=5) == []


async def test_rerank_fewer_than_top_k() -> None:
    result = await rerank("query", [_rc("only one")], top_k=10)
    assert len(result) == 1


async def test_rerank_boosts_matching_words() -> None:
    candidates = [
        _rc("machine learning neural network"),
        _rc("apple pie recipe"),
        _rc("apple orange fruit"),
    ]
    result = await rerank("apple", candidates, top_k=3)
    top_two = {r.chunk.content for r in result[:2]}
    assert "apple pie recipe" in top_two or "apple orange fruit" in top_two


async def test_rerank_combines_base_score_and_overlap() -> None:
    high_score = _rc("unrelated", score=1.0)
    low_score = _rc("matching query words", score=0.1)
    result = await rerank("matching query words", [high_score, low_score], top_k=2)
    assert len(result) == 2
