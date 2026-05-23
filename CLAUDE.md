# CLAUDE.md — Enterprise GenAI Platform

## Project overview
Demo project for the Ogmah GenAI engineer position. Full-stack RAG + agentic platform using OpenRouter, LangGraph, MCP, FastAPI, with production-grade observability and security.

## Tech stack
- **Python 3.12** — managed with `uv`
- **LLM gateway** — OpenRouter via `litellm` (env: `OPENROUTER_API_KEY`)
- **Vector store** — ChromaDB (local) / Azure AI Search (prod)
- **Agent framework** — LangGraph
- **MCP** — `mcp` Python SDK
- **API** — FastAPI + SSE streaming
- **Observability** — OpenTelemetry + Prometheus + Grafana + Jaeger
- **Security** — guardrails-ai + custom RBAC middleware
- **Testing** — pytest + RAGAS
- **Lint/format** — ruff + mypy
- **CI/CD** — GitHub Actions
- **Containers** — Docker multi-stage + docker-compose

## Key commands
```bash
make install      # install deps with uv
make lint         # ruff check + mypy
make test         # pytest with coverage
make run          # start FastAPI dev server
make docker-up    # full local stack (API + Prometheus + Grafana + Jaeger)
make docker-down  # tear down stack
make eval         # run RAGAS evaluation suite
make index        # index sample documents for dev
```

## Project structure
```
src/
  core/           # domain models, base interfaces
  rag/            # indexing + retrieval + generation
  agents/         # LangGraph supervisor + worker agents
  mcp/            # MCP server
  security/       # RBAC, guardrails, prompt shield
  observability/  # tracing, metrics, structured logging
  api/            # FastAPI app, routes, middleware
tests/
  unit/
  integration/
  evaluation/     # RAGAS eval suite
infra/
  docker/
  azure/          # Bicep templates
.github/workflows/
```

## Coding conventions
- Clean Architecture: no imports from outer layers into core/
- All LLM calls go through `src/core/llm_client.py` (never call litellm directly from business logic)
- Every public function must have a type annotation
- Use `structlog` for all logging (never `print`)
- Instrument every LLM + retrieval call with an OpenTelemetry span
- Secrets only via environment variables — never hardcoded

## Environment
Copy `.env.example` → `.env` and fill in your values before running anything.

## Running tests
```bash
make test                          # all tests
pytest tests/unit/ -v              # unit only
pytest tests/integration/ -v       # integration (needs running services)
pytest tests/evaluation/ -v        # RAGAS eval (needs OPENROUTER_API_KEY)
```

## Adding a new agent tool
1. Create `src/agents/tools/<tool_name>.py` implementing `BaseTool`
2. Register it in `src/agents/orchestrator.py`
3. Add unit tests in `tests/unit/agents/`
4. Document it in `ARCHITECTURE.md`
