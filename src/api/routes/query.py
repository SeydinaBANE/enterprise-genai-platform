from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.core.models import Role
from src.observability.logging import get_logger
from src.security.guardrails import ContentGuardrail
from src.security.prompt_shield import detect_injection
from src.security.rbac import TokenPayload, require_role

logger = get_logger(__name__)
router = APIRouter(prefix="/query", tags=["query"])

_guardrail = ContentGuardrail()


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)


class QueryResponse(BaseModel):
    question: str
    answer: str
    sources: list[dict[str, Any]]
    model: str
    latency_ms: float


@router.post("", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    user: Annotated[TokenPayload, Depends(require_role(Role.viewer, Role.editor, Role.admin))],
) -> QueryResponse:
    injected, msg = detect_injection(request.question)
    if injected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    ok, msg = await _guardrail.validate_input(request.question)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    from src.api.dependencies import get_hybrid_retriever, get_llm_client

    retriever = get_hybrid_retriever()
    llm = get_llm_client()

    from src.rag.generation.generator import generate_answer
    from src.rag.retrieval.reranker import rerank

    retrieved = await retriever.retrieve(request.question, top_k=request.top_k * 2)
    reranked = await rerank(request.question, retrieved, top_k=request.top_k)
    result = await generate_answer(request.question, reranked, llm)

    ok, msg = await _guardrail.validate_output(result.answer)
    if not ok:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=msg)

    logger.info("query_served", user=user.sub, latency_ms=round(result.latency_ms, 2))
    return QueryResponse(
        question=result.question,
        answer=result.answer,
        sources=[
            {
                "content": rc.chunk.content[:200],
                "score": rc.score,
                "source": rc.chunk.metadata.get("source"),
            }
            for rc in result.sources
        ],
        model=result.model,
        latency_ms=result.latency_ms,
    )
