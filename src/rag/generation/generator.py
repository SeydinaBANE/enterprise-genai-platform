from __future__ import annotations

import time

from src.core.interfaces import ILLMClient
from src.core.models import Message, QueryResult, RetrievedChunk
from src.observability.logging import get_logger
from src.observability.tracing import traced

logger = get_logger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based on provided context.

Rules:
- Answer only using the provided context. Do not use prior knowledge.
- If the context does not contain enough information, say so clearly.
- Always cite your sources by referencing the chunk index [1], [2], etc.
- Be concise and accurate.
"""


@traced("rag.generate")
async def generate_answer(
    question: str,
    retrieved: list[RetrievedChunk],
    llm_client: ILLMClient,
    model: str | None = None,
) -> QueryResult:
    start = time.perf_counter()

    context_parts = [
        f"[{i + 1}] (source: {rc.chunk.metadata.get('source', 'unknown')})\n{rc.chunk.content}"
        for i, rc in enumerate(retrieved)
    ]
    context = "\n\n".join(context_parts)

    messages = [
        Message(role="system", content=SYSTEM_PROMPT),
        Message(
            role="user",
            content=f"Context:\n{context}\n\nQuestion: {question}",
        ),
    ]

    response = await llm_client.complete(messages, model=model)
    latency_ms = (time.perf_counter() - start) * 1000

    logger.info("answer_generated", question_len=len(question), latency_ms=round(latency_ms, 2))

    return QueryResult(
        question=question,
        answer=response.content,
        sources=retrieved,
        model=response.model,
        latency_ms=latency_ms,
    )
