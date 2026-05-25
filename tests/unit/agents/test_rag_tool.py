from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

import src.agents.tools.rag_tool as rag_mod
from src.agents.tools.rag_tool import rag_query, set_retriever
from src.core.models import Chunk, RetrievedChunk
from src.rag.retrieval.hybrid import HybridRetriever


async def test_no_retriever_returns_not_available() -> None:
    rag_mod._retriever = None
    result = await rag_query.ainvoke({"question": "what?"})
    assert "not available" in result.lower()


async def test_wrong_retriever_type() -> None:
    rag_mod._retriever = object()
    result = await rag_query.ainvoke({"question": "what?"})
    assert "not properly configured" in result.lower()
    rag_mod._retriever = None


async def test_retriever_returns_results() -> None:
    mock_retriever = AsyncMock(spec=HybridRetriever)
    chunk = Chunk(id=uuid.uuid4(), document_id=uuid.uuid4(), content="relevant information")
    mock_retriever.retrieve.return_value = [
        RetrievedChunk(chunk=chunk, score=0.9, retrieval_method="hybrid")
    ]
    set_retriever(mock_retriever)

    result = await rag_query.ainvoke({"question": "relevant?"})
    assert "relevant information" in result
    rag_mod._retriever = None


async def test_retriever_empty_results() -> None:
    mock_retriever = AsyncMock(spec=HybridRetriever)
    mock_retriever.retrieve.return_value = []
    set_retriever(mock_retriever)

    result = await rag_query.ainvoke({"question": "obscure?"})
    assert "no relevant" in result.lower()
    rag_mod._retriever = None


def test_set_retriever_stores_reference() -> None:
    mock_retriever = AsyncMock(spec=HybridRetriever)
    set_retriever(mock_retriever)
    assert rag_mod._retriever is mock_retriever
    rag_mod._retriever = None
