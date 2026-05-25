from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

from src.core.models import Chunk, Document
from src.rag.indexing.pipeline import IndexingPipeline


async def test_index_document() -> None:
    llm = AsyncMock()
    store = AsyncMock()
    doc = Document(title="Test Doc", content="Hello world content here.", source="test.txt")

    async def mock_embed(chunks: list[Chunk], client: object) -> list[Chunk]:
        for c in chunks:
            c.embedding = [0.1, 0.2]
        return chunks

    with patch("src.rag.indexing.pipeline.embed_chunks", side_effect=mock_embed):
        pipeline = IndexingPipeline(llm, store)
        chunks = await pipeline.index(doc)

    assert len(chunks) > 0
    store.upsert.assert_called_once()


async def test_index_calls_embed() -> None:
    llm = AsyncMock()
    store = AsyncMock()
    doc = Document(title="Doc", content="Some content.", source="src.txt")

    embed_called = []

    async def mock_embed(chunks: list[Chunk], client: object) -> list[Chunk]:
        embed_called.append(True)
        for c in chunks:
            c.embedding = [0.0]
        return chunks

    with patch("src.rag.indexing.pipeline.embed_chunks", side_effect=mock_embed):
        pipeline = IndexingPipeline(llm, store)
        await pipeline.index(doc)

    assert embed_called


async def test_delete_document() -> None:
    llm = AsyncMock()
    store = AsyncMock()
    pipeline = IndexingPipeline(llm, store)
    doc_id = str(uuid.uuid4())
    await pipeline.delete(doc_id)
    store.delete_by_document.assert_called_once_with(doc_id)
