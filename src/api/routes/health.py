from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics", response_class=PlainTextResponse)
async def metrics() -> PlainTextResponse:
    return PlainTextResponse(generate_latest().decode(), media_type=CONTENT_TYPE_LATEST)
