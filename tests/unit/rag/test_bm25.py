import uuid

import pytest

from src.core.models import Chunk, Document
from src.rag.retrieval.bm25 import BM25Retriever


@pytest.fixture
def chunks() -> list[Chunk]:
    doc_id = uuid.uuid4()
    return [
        Chunk(document_id=doc_id, content="Azure OpenAI provides GPT models for enterprise use", chunk_index=0),
        Chunk(document_id=doc_id, content="LangGraph enables stateful multi-agent orchestration", chunk_index=1),
        Chunk(document_id=doc_id, content="RAG combines retrieval with language generation", chunk_index=2),
        Chunk(document_id=doc_id, content="Docker containers simplify deployment and scaling", chunk_index=3),
    ]


def test_bm25_retrieves_relevant_chunks(chunks: list[Chunk]) -> None:
    retriever = BM25Retriever()
    retriever.fit(chunks)
    results = retriever.retrieve("Azure OpenAI GPT", top_k=2)
    assert len(results) >= 1
    assert any("Azure" in r.content for r in results)


def test_bm25_returns_empty_before_fit() -> None:
    retriever = BM25Retriever()
    results = retriever.retrieve("test query")
    assert results == []


def test_bm25_top_k_limit(chunks: list[Chunk]) -> None:
    retriever = BM25Retriever()
    retriever.fit(chunks)
    results = retriever.retrieve("model agent", top_k=2)
    assert len(results) <= 2


def test_bm25_no_results_for_unrelated_query(chunks: list[Chunk]) -> None:
    retriever = BM25Retriever()
    retriever.fit(chunks)
    results = retriever.retrieve("xyzzy nonsense query zzz")
    assert len(results) == 0
