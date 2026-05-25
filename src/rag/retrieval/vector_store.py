from __future__ import annotations

import time
import uuid

import chromadb

from src.core.config import settings
from src.core.interfaces import ILLMClient
from src.core.models import Chunk
from src.observability.logging import get_logger
from src.observability.metrics import retrieval_latency_seconds, retrieval_results_count
from src.observability.tracing import traced

logger = get_logger(__name__)

COLLECTION_NAME = "genai_platform"


class ChromaRetriever:
    def __init__(self, llm_client: ILLMClient) -> None:
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        self._llm = llm_client

    @traced("chroma.retrieve")
    async def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        start = time.perf_counter()
        embeddings = await self._llm.embed([query])
        query_embedding = embeddings[0]

        results = self._collection.query(
            query_embeddings=[query_embedding],  # type: ignore[arg-type]
            n_results=min(top_k, max(1, self._collection.count())),
            include=["documents", "metadatas", "embeddings", "distances"],
        )

        latency = time.perf_counter() - start
        retrieval_latency_seconds.labels(store="chroma").observe(latency)

        chunks: list[Chunk] = []
        if not results["ids"] or not results["ids"][0]:
            return chunks

        for i, chunk_id in enumerate(results["ids"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            content = results["documents"][0][i] if results["documents"] else ""
            embedding = list(results["embeddings"][0][i]) if results["embeddings"] else []

            chunks.append(
                Chunk(
                    id=uuid.UUID(chunk_id) if _is_valid_uuid(chunk_id) else uuid.uuid4(),
                    document_id=uuid.UUID(str(meta.get("document_id", uuid.uuid4()))),
                    content=content,
                    embedding=embedding,
                    metadata=dict(meta),
                    chunk_index=int(meta.get("chunk_index", 0)),  # type: ignore[arg-type]
                )
            )

        retrieval_results_count.labels(store="chroma").observe(len(chunks))
        logger.info("chroma_retrieve", query_len=len(query), results=len(chunks))
        return chunks

    async def upsert(self, chunks: list[Chunk]) -> None:
        ids = [str(c.id) for c in chunks]
        documents = [c.content for c in chunks]
        embeddings = [c.embedding for c in chunks]
        metadatas = [
            {**c.metadata, "document_id": str(c.document_id), "chunk_index": c.chunk_index}
            for c in chunks
        ]
        self._collection.upsert(
            ids=ids,
            documents=documents,
            embeddings=embeddings,  # type: ignore[arg-type]
            metadatas=metadatas,  # type: ignore[arg-type]
        )
        logger.info("chroma_upsert", count=len(chunks))

    async def delete_by_document(self, document_id: str) -> None:
        self._collection.delete(where={"document_id": document_id})
        logger.info("chroma_delete", document_id=document_id)


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(value)
        return True
    except ValueError:
        return False
