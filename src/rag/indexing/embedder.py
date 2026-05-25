from __future__ import annotations

from src.core.interfaces import ILLMClient
from src.core.models import Chunk
from src.observability.logging import get_logger

logger = get_logger(__name__)

BATCH_SIZE = 32


async def embed_chunks(chunks: list[Chunk], client: ILLMClient) -> list[Chunk]:
    texts = [c.content for c in chunks]
    embeddings: list[list[float]] = []

    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i : i + BATCH_SIZE]
        batch_embeddings = await client.embed(batch)
        embeddings.extend(batch_embeddings)

    for chunk, embedding in zip(chunks, embeddings, strict=False):
        chunk.embedding = embedding

    logger.info("chunks_embedded", count=len(chunks))
    return chunks
