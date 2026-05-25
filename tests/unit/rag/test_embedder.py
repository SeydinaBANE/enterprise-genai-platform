from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

from src.core.models import Chunk
from src.rag.indexing.embedder import BATCH_SIZE, embed_chunks


def _chunk(content: str = "hello") -> Chunk:
    return Chunk(id=uuid.uuid4(), document_id=uuid.uuid4(), content=content)


async def test_embed_single_chunk() -> None:
    client = AsyncMock()
    client.embed.return_value = [[0.1, 0.2, 0.3]]
    chunks = [_chunk("test text")]
    result = await embed_chunks(chunks, client)
    assert result[0].embedding == [0.1, 0.2, 0.3]
    client.embed.assert_called_once_with(["test text"])


async def test_embed_empty_list() -> None:
    client = AsyncMock()
    result = await embed_chunks([], client)
    assert result == []
    client.embed.assert_not_called()


async def test_embed_batches_large_input() -> None:
    n = BATCH_SIZE + 5
    client = AsyncMock()
    client.embed.side_effect = [
        [[float(i)] for i in range(BATCH_SIZE)],
        [[float(i)] for i in range(5)],
    ]
    chunks = [_chunk(f"text {i}") for i in range(n)]
    result = await embed_chunks(chunks, client)
    assert len(result) == n
    assert client.embed.call_count == 2


async def test_embed_sets_embedding_on_chunk() -> None:
    client = AsyncMock()
    embedding = [0.5, 0.6, 0.7]
    client.embed.return_value = [embedding]
    chunks = [_chunk("content")]
    result = await embed_chunks(chunks, client)
    assert result[0].embedding == embedding
    assert result[0] is chunks[0]  # same object mutated in place
