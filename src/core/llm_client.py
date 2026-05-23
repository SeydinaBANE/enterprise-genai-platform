from __future__ import annotations

import time

import litellm
from tenacity import retry, stop_after_attempt, wait_exponential

from src.core.config import settings
from src.core.models import LLMResponse, Message
from src.observability.logging import get_logger
from src.observability.metrics import llm_calls_total, llm_latency_seconds, token_usage_total
from src.observability.tracing import traced

logger = get_logger(__name__)

litellm.api_base = settings.litellm_api_base
litellm.api_key = settings.openrouter_api_key


class LLMClient:
    def __init__(self, default_model: str | None = None) -> None:
        self._model = default_model or settings.llm_model
        self._embedding_model = settings.embedding_model

    @traced("llm.complete")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        target_model = model or self._model
        start = time.perf_counter()
        try:
            response = await litellm.acompletion(
                model=target_model,
                messages=[m.model_dump() for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
                api_base=settings.litellm_api_base,
                api_key=settings.openrouter_api_key,
            )
            latency = (time.perf_counter() - start) * 1000
            usage = response.usage

            llm_calls_total.labels(model=target_model, status="success").inc()
            llm_latency_seconds.labels(model=target_model).observe(latency / 1000)
            token_usage_total.labels(model=target_model, type="prompt").inc(usage.prompt_tokens)
            token_usage_total.labels(model=target_model, type="completion").inc(
                usage.completion_tokens
            )

            logger.info(
                "llm_complete",
                model=target_model,
                latency_ms=round(latency, 2),
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                model=target_model,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                finish_reason=response.choices[0].finish_reason,
            )
        except Exception as exc:
            llm_calls_total.labels(model=target_model, status="error").inc()
            logger.error("llm_complete_error", model=target_model, error=str(exc))
            raise

    @traced("llm.embed")
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def embed(self, texts: list[str]) -> list[list[float]]:
        start = time.perf_counter()
        try:
            response = await litellm.aembedding(
                model=self._embedding_model,
                input=texts,
                api_base=settings.litellm_api_base,
                api_key=settings.openrouter_api_key,
            )
            latency = (time.perf_counter() - start) * 1000
            logger.info("llm_embed", count=len(texts), latency_ms=round(latency, 2))
            return [item["embedding"] for item in response.data]
        except Exception as exc:
            logger.error("llm_embed_error", error=str(exc))
            raise
