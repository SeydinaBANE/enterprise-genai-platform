from __future__ import annotations

from src.core.interfaces import ILLMClient
from src.core.models import Chunk, Document
from src.observability.logging import get_logger
from src.rag.indexing.chunker import chunk_document
from src.rag.indexing.embedder import embed_chunks
from src.rag.retrieval.vector_store import ChromaRetriever

logger = get_logger(__name__)


class IndexingPipeline:
    def __init__(self, llm_client: ILLMClient, vector_store: ChromaRetriever) -> None:
        self._llm = llm_client
        self._store = vector_store

    async def index(self, document: Document) -> list[Chunk]:
        logger.info("indexing_start", doc_id=str(document.id), title=document.title)

        chunks = chunk_document(document)
        chunks = await embed_chunks(chunks, self._llm)
        await self._store.upsert(chunks)

        logger.info("indexing_done", doc_id=str(document.id), chunks=len(chunks))
        return chunks

    async def delete(self, document_id: str) -> None:
        await self._store.delete_by_document(document_id)
        logger.info("document_deleted", doc_id=document_id)
