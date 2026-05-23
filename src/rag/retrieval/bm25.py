from __future__ import annotations

import re

from rank_bm25 import BM25Okapi

from src.core.models import Chunk
from src.observability.logging import get_logger

logger = get_logger(__name__)


def _tokenize(text: str) -> list[str]:
    return re.findall(r"\b\w+\b", text.lower())


class BM25Retriever:
    def __init__(self) -> None:
        self._corpus: list[Chunk] = []
        self._bm25: BM25Okapi | None = None

    def fit(self, chunks: list[Chunk]) -> None:
        self._corpus = chunks
        tokenized = [_tokenize(c.content) for c in chunks]
        self._bm25 = BM25Okapi(tokenized)
        logger.info("bm25_fit", corpus_size=len(chunks))

    def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]:
        if self._bm25 is None or not self._corpus:
            return []

        tokens = _tokenize(query)
        scores = self._bm25.get_scores(tokens)

        ranked = sorted(
            zip(scores, self._corpus),
            key=lambda x: x[0],
            reverse=True,
        )
        results = [chunk for _, chunk in ranked[:top_k] if _ > 0]
        logger.info("bm25_retrieve", query_len=len(query), results=len(results))
        return results
