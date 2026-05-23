from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Role(str, Enum):
    viewer = "viewer"
    editor = "editor"
    admin = "admin"


class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    content: str
    source: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Chunk(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    content: str
    embedding: list[float] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    chunk_index: int = 0


class RetrievedChunk(BaseModel):
    chunk: Chunk
    score: float
    retrieval_method: str


class Message(BaseModel):
    role: str  # "system" | "user" | "assistant"
    content: str


class LLMResponse(BaseModel):
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class QueryResult(BaseModel):
    question: str
    answer: str
    sources: list[RetrievedChunk]
    model: str
    latency_ms: float


class AgentResult(BaseModel):
    task: str
    output: str
    steps: list[dict[str, Any]] = Field(default_factory=list)
    model: str
    latency_ms: float
