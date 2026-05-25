from __future__ import annotations

from unittest.mock import patch

from src.api.dependencies import (
    get_bm25,
    get_hybrid_retriever,
    get_indexing_pipeline,
    get_llm_client,
    get_vector_store,
)
from src.core.llm_client import LLMClient
from src.rag.indexing.pipeline import IndexingPipeline
from src.rag.retrieval.bm25 import BM25Retriever
from src.rag.retrieval.hybrid import HybridRetriever
from src.rag.retrieval.vector_store import ChromaRetriever


def test_get_llm_client_returns_instance() -> None:
    get_llm_client.cache_clear()
    client = get_llm_client()
    assert isinstance(client, LLMClient)


def test_get_llm_client_cached() -> None:
    get_llm_client.cache_clear()
    assert get_llm_client() is get_llm_client()


def test_get_bm25_returns_instance() -> None:
    get_bm25.cache_clear()
    bm25 = get_bm25()
    assert isinstance(bm25, BM25Retriever)


def test_get_vector_store_with_mock_chroma() -> None:
    get_vector_store.cache_clear()
    get_llm_client.cache_clear()
    with patch("chromadb.PersistentClient"):
        store = get_vector_store()
    assert isinstance(store, ChromaRetriever)


def test_get_hybrid_retriever_with_mock_chroma() -> None:
    get_hybrid_retriever.cache_clear()
    get_vector_store.cache_clear()
    get_bm25.cache_clear()
    get_llm_client.cache_clear()
    with patch("chromadb.PersistentClient"):
        retriever = get_hybrid_retriever()
    assert isinstance(retriever, HybridRetriever)


def test_get_indexing_pipeline_with_mock_chroma() -> None:
    get_indexing_pipeline.cache_clear()
    get_vector_store.cache_clear()
    get_llm_client.cache_clear()
    with patch("chromadb.PersistentClient"):
        pipeline = get_indexing_pipeline()
    assert isinstance(pipeline, IndexingPipeline)
