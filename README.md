# Enterprise GenAI Platform

Production-grade GenAI platform demo showcasing RAG, multi-agent orchestration, MCP, observability, and security — built for the Ogmah GenAI engineer position.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        FastAPI (REST + SSE)                   │
│          /index   /query   /agent/run   /health              │
└──────────────┬───────────────────┬──────────────────────────┘
               │                   │
    ┌──────────▼──────┐   ┌────────▼────────────────────────┐
    │   RAG Pipeline   │   │   LangGraph Agent Orchestrator   │
    │                  │   │                                  │
    │  Loader          │   │  Supervisor                      │
    │  Chunker         │   │   ├── Researcher Agent           │
    │  Embedder        │   │   └── Analyst Agent              │
    │  HybridRetriever │   │                                  │
    │  Reranker        │   │  Tools:                          │
    │  Generator       │   │   ├── rag_tool                   │
    └──────────┬───────┘   │   ├── web_search_tool            │
               │           │   └── code_exec_tool             │
    ┌──────────▼───────┐   └────────────────┬────────────────┘
    │   ChromaDB        │                    │
    │   (vector store)  │   ┌───────────────▼──────────────┐
    └──────────────────┘   │   MCP Server                  │
                            │   tools: rag_query, run_agent │
                            └──────────────────────────────┘

┌────────────────────────────────────────────────────────────┐
│                     Cross-cutting Concerns                  │
│  Security: RBAC · Guardrails · Prompt Shield               │
│  Observability: OpenTelemetry · Prometheus · Grafana       │
│  Logging: structlog JSON                                    │
└────────────────────────────────────────────────────────────┘
```

## Stack

| Layer | Technology |
|-------|-----------|
| LLM Gateway | OpenRouter via `litellm` |
| Vector Store | ChromaDB (local) / Azure AI Search (prod) |
| Agents | LangGraph |
| MCP | `mcp` Python SDK |
| API | FastAPI + SSE |
| Observability | OpenTelemetry + Prometheus + Grafana + Jaeger |
| Security | guardrails-ai + custom RBAC |
| Testing | pytest + RAGAS |
| CI/CD | GitHub Actions |
| Containers | Docker + docker-compose |

## Quickstart

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- Docker + Docker Compose
- OpenRouter API key

### Local setup

```bash
# 1. Clone & install
git clone <repo>
cd projet-2
make install

# 2. Configure
cp .env.example .env
# Edit .env — add OPENROUTER_API_KEY

# 3. Start local stack
make docker-up

# 4. Index sample documents
make index

# 5. Try it
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key risks?", "top_k": 5}'
```

### Run agent
```bash
curl -X POST http://localhost:8000/agent/run \
  -H "Content-Type: application/json" \
  -d '{"task": "Research and summarize the main themes across all documents"}'
```

### Services (after `make docker-up`)

| Service | URL |
|---------|-----|
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Prometheus | http://localhost:9090 |
| Grafana | http://localhost:3000 |
| Jaeger | http://localhost:16686 |

## Development

```bash
make lint      # ruff + mypy
make test      # pytest + coverage
make eval      # RAGAS evaluation suite
```

## Project structure

```
src/
  core/           # domain models + interfaces
  rag/            # indexing, retrieval, generation
  agents/         # LangGraph supervisor + tools
  mcp/            # MCP server
  security/       # RBAC, guardrails, prompt shield
  observability/  # tracing, metrics, logging
  api/            # FastAPI app
tests/
  unit/
  integration/
  evaluation/
infra/
  docker/         # Prometheus, Grafana, Jaeger configs
  azure/          # Bicep templates
.github/
  workflows/      # CI + CD
```

## Security design

- **RBAC** — JWT-based roles (viewer / editor / admin) enforced at API layer
- **Guardrails** — input and output content filtering on every LLM call
- **Prompt shield** — injection detection before sending to LLM
- **Secrets** — environment variables only, never in code or logs

## Observability

- Every LLM call is traced (model, tokens, latency)
- Every retrieval call is traced (query, top-k, scores)
- Prometheus metrics: `llm_calls_total`, `retrieval_latency_seconds`, `token_usage_total`
- Grafana dashboard included in `infra/docker/grafana/`
- Structured JSON logs with trace correlation IDs

## Evaluation

RAGAS metrics tracked per release:
- **Faithfulness** — answers grounded in retrieved context
- **Answer relevance** — answers address the question
- **Context precision** — retrieved chunks are relevant

```bash
make eval   # runs full RAGAS suite, prints scores
```
