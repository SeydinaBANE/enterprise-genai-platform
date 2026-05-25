from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.models import Chunk
from src.rag.retrieval.vector_store import ChromaRetriever, _is_valid_uuid


def test_is_valid_uuid_true() -> None:
    assert _is_valid_uuid(str(uuid.uuid4())) is True


def test_is_valid_uuid_false() -> None:
    assert _is_valid_uuid("not-a-uuid") is False
    assert _is_valid_uuid("") is False


def _build_retriever() -> tuple[ChromaRetriever, MagicMock, AsyncMock]:
    llm = AsyncMock()
    with patch("chromadb.PersistentClient") as mock_client_cls:
        mock_col = MagicMock()
        mock_client_cls.return_value.get_or_create_collection.return_value = mock_col
        r = ChromaRetriever(llm)
    return r, mock_col, llm


async def test_retrieve_empty_collection() -> None:
    retriever, mock_col, llm = _build_retriever()
    llm.embed.return_value = [[0.1, 0.2]]
    mock_col.count.return_value = 0
    mock_col.query.return_value = {
        "ids": [[]],
        "metadatas": [[]],
        "documents": [[]],
        "embeddings": [[]],
    }
    results = await retriever.retrieve("test query")
    assert results == []


async def test_retrieve_with_results() -> None:
    retriever, mock_col, llm = _build_retriever()
    chunk_id = str(uuid.uuid4())
    doc_id = str(uuid.uuid4())
    llm.embed.return_value = [[0.1, 0.2]]
    mock_col.count.return_value = 1
    mock_col.query.return_value = {
        "ids": [[chunk_id]],
        "metadatas": [[{"document_id": doc_id, "chunk_index": 0, "source": "test.txt"}]],
        "documents": [["hello world"]],
        "embeddings": [[[0.1, 0.2]]],
    }
    results = await retriever.retrieve("query")
    assert len(results) == 1
    assert results[0].content == "hello world"


async def test_upsert_chunks() -> None:
    retriever, mock_col, _llm = _build_retriever()
    chunk = Chunk(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        content="test content",
        embedding=[0.1, 0.2],
    )
    await retriever.upsert([chunk])
    mock_col.upsert.assert_called_once()


async def test_delete_by_document() -> None:
    retriever, mock_col, _llm = _build_retriever()
    await retriever.delete_by_document("some-doc-id")
    mock_col.delete.assert_called_once_with(where={"document_id": "some-doc-id"})


async def test_retrieve_invalid_uuid_gets_new_id() -> None:
    retriever, mock_col, llm = _build_retriever()
    llm.embed.return_value = [[0.1]]
    doc_id = str(uuid.uuid4())
    mock_col.count.return_value = 1
    mock_col.query.return_value = {
        "ids": [["not-a-valid-uuid"]],
        "metadatas": [[{"document_id": doc_id, "chunk_index": 0}]],
        "documents": [["content"]],
        "embeddings": [[[0.1]]],
    }
    results = await retriever.retrieve("q")
    assert len(results) == 1
