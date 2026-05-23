from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.core.models import Chunk, Document, LLMResponse, Message


@runtime_checkable
class ILLMClient(Protocol):
    async def complete(
        self,
        messages: list[Message],
        model: str | None = None,
        temperature: float = 0.0,
        max_tokens: int = 2048,
    ) -> LLMResponse: ...

    async def embed(self, texts: list[str]) -> list[list[float]]: ...


@runtime_checkable
class IIndexer(Protocol):
    async def index(self, document: Document) -> list[Chunk]: ...

    async def delete(self, document_id: str) -> None: ...


@runtime_checkable
class IRetriever(Protocol):
    async def retrieve(self, query: str, top_k: int = 5) -> list[Chunk]: ...


@runtime_checkable
class IGuardrail(Protocol):
    async def validate_input(self, text: str) -> tuple[bool, str]: ...

    async def validate_output(self, text: str) -> tuple[bool, str]: ...
