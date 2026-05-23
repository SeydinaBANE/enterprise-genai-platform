from __future__ import annotations

from functools import lru_cache

from src.core.llm_client import LLMClient
from src.rag.indexing.pipeline import IndexingPipeline
from src.rag.retrieval.bm25 import BM25Retriever
from src.rag.retrieval.hybrid import HybridRetriever
from src.rag.retrieval.vector_store import ChromaRetriever


@lru_cache(maxsize=1)
def get_llm_client() -> LLMClient:
    return LLMClient()


@lru_cache(maxsize=1)
def get_vector_store() -> ChromaRetriever:
    return ChromaRetriever(get_llm_client())


@lru_cache(maxsize=1)
def get_bm25() -> BM25Retriever:
    return BM25Retriever()


@lru_cache(maxsize=1)
def get_hybrid_retriever() -> HybridRetriever:
    return HybridRetriever(get_vector_store(), get_bm25())


@lru_cache(maxsize=1)
def get_indexing_pipeline() -> IndexingPipeline:
    return IndexingPipeline(get_llm_client(), get_vector_store())
