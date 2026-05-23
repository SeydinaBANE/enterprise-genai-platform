from __future__ import annotations

from src.core.models import Chunk, Document
from src.observability.logging import get_logger

logger = get_logger(__name__)

DEFAULT_CHUNK_SIZE = 512
DEFAULT_OVERLAP = 64


def chunk_document(
    document: Document,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[Chunk]:
    text = document.content
    chunks: list[Chunk] = []
    separators = ["\n\n", "\n", ". ", " ", ""]

    raw_chunks = _recursive_split(text, separators, chunk_size)

    start = 0
    for i, raw in enumerate(raw_chunks):
        if i > 0:
            prev_end = sum(len(c) for c in raw_chunks[:i])
            start = max(0, prev_end - overlap)

        chunks.append(
            Chunk(
                document_id=document.id,
                content=raw.strip(),
                chunk_index=i,
                metadata={
                    "source": document.source,
                    "title": document.title,
                    "char_start": start,
                },
            )
        )

    logger.info("document_chunked", doc_id=str(document.id), chunks=len(chunks))
    return [c for c in chunks if c.content]


def _recursive_split(text: str, separators: list[str], max_size: int) -> list[str]:
    if len(text) <= max_size:
        return [text]

    sep = next((s for s in separators if s and s in text), "")

    if not sep:
        return [text[i : i + max_size] for i in range(0, len(text), max_size)]

    parts = text.split(sep)
    merged: list[str] = []
    current = ""

    for part in parts:
        candidate = current + sep + part if current else part
        if len(candidate) <= max_size:
            current = candidate
        else:
            if current:
                merged.append(current)
            if len(part) > max_size:
                next_seps = separators[separators.index(sep) + 1 :]
                merged.extend(_recursive_split(part, next_seps, max_size))
                current = ""
            else:
                current = part

    if current:
        merged.append(current)

    return merged
