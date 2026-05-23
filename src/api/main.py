from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routes import agent, documents, health, query
from src.observability.logging import configure_logging
from src.observability.tracing import configure_tracing


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    configure_logging()
    configure_tracing()
    yield


app = FastAPI(
    title="Enterprise GenAI Platform",
    description="RAG + Multi-Agent + MCP platform with full observability and security",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(agent.router)
