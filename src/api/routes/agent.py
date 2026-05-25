from __future__ import annotations

import asyncio
import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.agents.orchestrator import run_agent
from src.core.models import Role
from src.observability.logging import get_logger
from src.security.guardrails import ContentGuardrail
from src.security.prompt_shield import detect_injection
from src.security.rbac import TokenPayload, require_role

logger = get_logger(__name__)
router = APIRouter(prefix="/agent", tags=["agent"])

_guardrail = ContentGuardrail()


class AgentRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=4000)
    stream: bool = False


class AgentResponse(BaseModel):
    task: str
    output: str
    steps: list[dict[str, Any]]
    model: str
    latency_ms: float


@router.post("/run", response_model=AgentResponse)
async def agent_run(
    request: AgentRequest,
    user: Annotated[TokenPayload, Depends(require_role(Role.editor, Role.admin))],
) -> AgentResponse | StreamingResponse:
    injected, msg = detect_injection(request.task)
    if injected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    ok, msg = await _guardrail.validate_input(request.task)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

    if request.stream:
        return _stream_agent(request.task, user.sub)

    result = await run_agent(request.task)
    logger.info("agent_run_served", user=user.sub, latency_ms=round(result.latency_ms, 2))
    return AgentResponse(**result.model_dump())


def _stream_agent(task: str, user_sub: str) -> StreamingResponse:
    async def generator() -> object:
        result = await run_agent(task)
        words = result.output.split()
        for word in words:
            yield f"data: {json.dumps({'token': word + ' '})}\n\n"
            await asyncio.sleep(0.02)
        yield f"data: {json.dumps({'done': True, 'model': result.model})}\n\n"

    return StreamingResponse(generator(), media_type="text/event-stream")
