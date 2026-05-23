# TODO — Enterprise GenAI Platform

## Phase 0 — Documentation & Scaffold
- [x] CLAUDE.md
- [x] TODO.md
- [x] README.md
- [x] ARCHITECTURE.md
- [x] Makefile
- [x] .env.example
- [x] pyproject.toml (uv, ruff, mypy, pytest)
- [x] .gitignore
- [ ] pre-commit config
- [x] Project directory structure (src/, tests/, infra/)

## Phase 1 — Core RAG Pipeline
- [x] `src/core/models.py` — Document, Chunk, QueryResult domain models
- [x] `src/core/interfaces.py` — IRetriever, IIndexer, ILLMClient abstract interfaces
- [x] `src/core/llm_client.py` — OpenRouter via litellm, with retry + token counting
- [x] `src/rag/indexing/loader.py` — PDF, TXT, MD document loaders
- [x] `src/rag/indexing/chunker.py` — recursive text splitter with overlap
- [x] `src/rag/indexing/embedder.py` — embedding via OpenRouter (text-embedding-3-small)
- [x] `src/rag/indexing/pipeline.py` — orchestrates load → chunk → embed → store
- [x] `src/rag/retrieval/vector_store.py` — ChromaDB adapter
- [x] `src/rag/retrieval/bm25.py` — BM25 keyword retrieval
- [x] `src/rag/retrieval/hybrid.py` — RRF fusion of semantic + BM25
- [x] `src/rag/retrieval/reranker.py` — cross-encoder reranking
- [x] `src/rag/generation/generator.py` — answer synthesis with source citations
- [x] Unit tests for all RAG components

## Phase 2 — Agentic Layer (LangGraph)
- [x] `src/agents/tools/rag_tool.py` — RAG query as LangGraph tool
- [x] `src/agents/tools/web_search_tool.py` — mock/DuckDuckGo web search
- [x] `src/agents/tools/code_exec_tool.py` — sandboxed Python execution
- [ ] `src/agents/researcher.py` — research agent node (inline in orchestrator)
- [ ] `src/agents/analyst.py` — analysis + synthesis agent node
- [x] `src/agents/orchestrator.py` — LangGraph supervisor graph
- [x] `src/agents/state.py` — shared state schema
- [x] Unit tests for code_exec tool

## Phase 3 — MCP Server
- [x] `src/mcp/server.py` — MCP server with tools: `rag_query`, `run_agent`, `list_documents`
- [ ] Integration test: connect Claude Desktop to local MCP server

## Phase 4 — Security
- [x] `src/security/rbac.py` — role definitions (viewer, editor, admin) + FastAPI dependency
- [x] `src/security/guardrails.py` — input/output content filtering
- [x] `src/security/prompt_shield.py` — prompt injection detection heuristics
- [ ] `src/api/middleware/auth.py` — JWT verification middleware (inline in rbac.py)
- [x] Tests for security layer

## Phase 5 — Observability
- [x] `src/observability/logging.py` — structlog JSON config
- [x] `src/observability/tracing.py` — OpenTelemetry tracer setup + decorators
- [x] `src/observability/metrics.py` — Prometheus counters + histograms
- [x] Instrument all LLM + retrieval calls
- [ ] `infra/docker/grafana/` — dashboard provisioning JSON (Grafana container included)

## Phase 6 — FastAPI
- [x] `src/api/main.py` — app factory
- [x] `src/api/routes/documents.py` — POST /documents/index
- [x] `src/api/routes/query.py` — POST /query (RAG)
- [x] `src/api/routes/agent.py` — POST /agent/run, streaming SSE
- [x] `src/api/routes/health.py` — GET /health, GET /metrics
- [x] `src/api/dependencies.py` — dependency injection

## Phase 7 — Evaluation
- [x] `tests/evaluation/ragas_suite.py` — faithfulness + answer relevance tests
- [ ] `tests/evaluation/fixtures/` — sample Q&A pairs for eval
- [x] `make eval` target in Makefile

## Phase 8 — CI/CD
- [x] `.github/workflows/ci.yml` — lint → test → coverage ≥ 80%
- [x] `.github/workflows/cd.yml` — Docker build → push GHCR on main
- [x] `Dockerfile` — multi-stage build (builder + runtime)
- [x] `docker-compose.yml` — API + Prometheus + Grafana + Jaeger + OTel Collector

## Phase 9 — Azure (optional, for prod demo)
- [ ] `infra/azure/main.bicep` — Azure OpenAI + AI Search + Container Apps
- [ ] `src/rag/retrieval/azure_search.py` — Azure AI Search adapter
- [ ] Managed Identity auth pattern documented in ARCHITECTURE.md
