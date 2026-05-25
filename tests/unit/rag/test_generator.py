from __future__ import annotations

import uuid
from unittest.mock import AsyncMock

from src.core.models import Chunk, LLMResponse, RetrievedChunk
from src.rag.generation.generator import generate_answer


def _rc(content: str, source: str = "test.txt") -> RetrievedChunk:
    chunk = Chunk(
        id=uuid.uuid4(),
        document_id=uuid.uuid4(),
        content=content,
        metadata={"source": source},
    )
    return RetrievedChunk(chunk=chunk, score=0.9, retrieval_method="hybrid")


def _llm_response(text: str = "The answer.", model: str = "gpt-4o-mini") -> LLMResponse:
    return LLMResponse(
        content=text, model=model, prompt_tokens=50, completion_tokens=10, finish_reason="stop"
    )


async def test_generate_with_context() -> None:
    llm = AsyncMock()
    llm.complete.return_value = _llm_response()
    result = await generate_answer("What is X?", [_rc("context info")], llm)
    assert result.answer == "The answer."
    assert result.question == "What is X?"
    assert len(result.sources) == 1


async def test_generate_empty_context() -> None:
    llm = AsyncMock()
    llm.complete.return_value = _llm_response("I don't know.")
    result = await generate_answer("Obscure?", [], llm)
    assert result.answer == "I don't know."
    assert result.sources == []


async def test_generate_passes_model_kwarg() -> None:
    llm = AsyncMock()
    llm.complete.return_value = _llm_response(model="custom-model")
    await generate_answer("Q", [], llm, model="custom-model")
    _, kwargs = llm.complete.call_args
    assert kwargs.get("model") == "custom-model"


async def test_generate_latency_is_positive() -> None:
    llm = AsyncMock()
    llm.complete.return_value = _llm_response()
    result = await generate_answer("Q", [], llm)
    assert result.latency_ms >= 0
