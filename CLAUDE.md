# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview
Demo project for the Ogmah GenAI engineer position. Full-stack RAG + agentic platform using OpenRouter, LangGraph, MCP, FastAPI, with production-grade observability and security.

## Tech stack
- **Python 3.12** — managed with `uv`
- **LLM gateway** — OpenRouter via `litellm` (env: `OPENROUTER_API_KEY`)
- **Vector store** — ChromaDB (local) / Azure AI Search (prod), auto-selected via `settings.use_azure_search`
- **Agent framework** — LangGraph
- **MCP** — `mcp` Python SDK, stdio transport
- **API** — FastAPI + SSE streaming
- **Observability** — OpenTelemetry + Prometheus + Grafana + Jaeger
- **Security** — guardrails-ai + custom RBAC middleware
- **Testing** — pytest + RAGAS
- **Lint/format** — ruff + mypy

## Key commands
```bash
make install           # install deps with uv
make lint              # ruff check + mypy
make format            # ruff format + autofix
make test              # pytest unit + integration with coverage (min 80%)
make test-unit         # unit tests only
make test-integration  # integration tests (needs running services)
make run               # start FastAPI dev server on :8000
make docker-up         # full local stack (API + ChromaDB + Prometheus + Grafana + Jaeger)
make docker-down       # tear down stack
make eval              # RAGAS evaluation suite (needs OPENROUTER_API_KEY)
make index             # index sample documents for dev
make clean             # remove __pycache__, .coverage, .mypy_cache, etc.
```

Single test: `uv run pytest tests/unit/rag/test_chunker.py -v`

Generate a JWT for local API testing:
```bash
uv run python scripts/create_token.py --role editor   # roles: viewer | editor | admin
# then: curl -H "Authorization: Bearer <token>" http://localhost:8000/query ...
```

MCP server (stdio transport, not HTTP):
```bash
uv run python -m src.mcp.server
```

## Architecture

### Layer dependency rule
```
src/api  →  src/agents, src/rag, src/security, src/observability
src/agents  →  src/core, src/rag, src/observability
src/rag     →  src/core, src/observability
src/mcp     →  src/agents, src/rag
src/security→  src/core
src/observability → (none)
src/core    → (none — pure domain, no internal imports)
```
`src/core` never imports from any other `src/` module.

### Core contracts (`src/core/interfaces.py`)
All cross-layer dependencies are expressed as `Protocol` interfaces. Implementations live in adapter modules; the core only knows the protocol.

### RAG pipeline
```
Indexing:   loader → chunker → embedder → ChromaRetriever (or AzureSearch)
Retrieval:  ChromaRetriever (cosine) + BM25Retriever → RRF fusion → reranker → top-k chunks
Generation: chunks + prompt → LLMClient.complete() → QueryResult with citations
```
Sub-modules: `src/rag/indexing/`, `src/rag/retrieval/`, `src/rag/generation/`.
The `HybridRetriever` in `src/rag/retrieval/hybrid.py` wires vector + BM25 + RRF + reranker.

### Agent orchestration (`src/agents/orchestrator.py`)
Single LangGraph `StateGraph` with two nodes: `agent` (LLM with tool-calling) and `tools` (`ToolNode`). The graph loops until no tool calls remain. Registered tools:
- `rag_query` — searches the knowledge base
- `web_search` — live web search
- `execute_python` — sandboxed code execution

To add a tool: implement it as a LangChain `@tool` in `src/agents/tools/`, append it to the `TOOLS` list in `orchestrator.py`, add unit tests in `tests/unit/agents/`, and document it in `ARCHITECTURE.md`.

### API routes (`src/api/routes/`)
- `GET /health` — liveness check
- `POST /documents` — index a document (`editor`+ role)
- `POST /query` — RAG query (`viewer`+ role)
- `POST /agent` — multi-step agent run (`editor`+ role)

Singletons for all service dependencies are managed with `@lru_cache` in `src/api/dependencies.py`.

### Security layers (request order)
JWT auth + RBAC (`src/security/rbac.py`) → prompt injection shield (`src/security/prompt_shield.py`) → input guardrails → LLM call → output guardrails.

RBAC roles: `viewer` (read-only), `editor` (index + agents), `admin` (full).

### Observability
Use the `@traced("span.name")` decorator from `src/observability/tracing.py` on every async function that performs I/O. It creates an OTel span and records exceptions automatically.

Use `get_logger(__name__)` from `src/observability/logging.py` (structlog); never `print` or stdlib `logging` directly.

## Coding conventions
- Clean Architecture: no imports from outer layers into `src/core/`
- All LLM calls go through `src/core/llm_client.py` (never call `litellm` directly from business logic)
- Every public function must have a type annotation
- Instrument every LLM + retrieval call with `@traced`

## Environment
Copy `.env.example` → `.env` and fill in your values before running anything.
Key vars: `OPENROUTER_API_KEY`, `JWT_SECRET_KEY` (default `change_me`), `CHROMA_PERSIST_DIR`.
