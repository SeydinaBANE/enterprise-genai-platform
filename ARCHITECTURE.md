# Architecture — Enterprise GenAI Platform

## Design principles

- **Clean Architecture** — domain core has zero external dependencies; adapters (LLM, vector store, API) depend inward
- **Dependency inversion** — all external services are accessed through interfaces defined in `src/core/interfaces.py`
- **Observability first** — every I/O operation carries a trace span; no silent failures
- **Security by design** — guardrails and RBAC are enforced at the boundary, not sprinkled throughout

---

## Data flow

### RAG query

```
User Request
    │
    ▼
[Auth Middleware]  ── JWT validation + RBAC check
    │
    ▼
[Prompt Shield]    ── injection detection
    │
    ▼
[Input Guardrails] ── content filtering
    │
    ▼
[Hybrid Retriever]
    ├── ChromaDB semantic search  (cosine similarity)
    └── BM25 keyword search
         │
         ▼
    [RRF Fusion]   ── reciprocal rank fusion
         │
         ▼
    [Reranker]     ── cross-encoder scoring
         │
         ▼
[Generator]        ── OpenRouter LLM with system prompt + context
    │
    ▼
[Output Guardrails] ── content filtering on response
    │
    ▼
Response with citations
```

### Agent run

```
User Task
    │
    ▼
[LangGraph Supervisor]
    │
    ├──► Researcher Agent
    │         └── Tools: rag_tool, web_search_tool
    │
    └──► Analyst Agent
              └── Tools: rag_tool, code_exec_tool
    │
    ▼
[Synthesis]   ── supervisor merges outputs
    │
    ▼
Streamed Response (SSE)
```

---

## Module dependencies

```
src/api          →  src/agents, src/rag, src/security, src/observability
src/agents       →  src/core, src/rag, src/observability
src/rag          →  src/core, src/observability
src/mcp          →  src/agents, src/rag
src/security     →  src/core
src/observability→  (no internal deps)
src/core         →  (no internal deps — pure domain)
```

**Rule:** arrows point inward only. `src/core` never imports from other src modules.

---

## Key interfaces (`src/core/interfaces.py`)

```python
class ILLMClient(Protocol):
    async def complete(self, messages: list[Message], **kwargs) -> LLMResponse: ...
    async def embed(self, texts: list[str]) -> list[list[float]]: ...

class IRetriever(Protocol):
    async def retrieve(self, query: str, top_k: int) -> list[Chunk]: ...

class IIndexer(Protocol):
    async def index(self, document: Document) -> None: ...
```

---

## ADR (Architecture Decision Records)

### ADR-001: OpenRouter over direct Azure OpenAI
**Decision:** Use OpenRouter via `litellm` as the LLM gateway.
**Reason:** Allows model switching (GPT-4o, Claude, Mistral) without code changes; same interface in dev and prod.
**Trade-off:** Extra network hop; mitigated by async calls and retry logic.

### ADR-002: ChromaDB for local, Azure AI Search for prod
**Decision:** Abstract vector store behind `IRetriever`; swap implementation via config.
**Reason:** Zero-cost local development; production uses Azure AI Search for hybrid search + enterprise SLA.
**Trade-off:** Feature parity not 100% (Azure AI Search has richer filtering).

### ADR-003: LangGraph over raw LangChain
**Decision:** Use LangGraph for agent orchestration.
**Reason:** Explicit state machine makes control flow testable and debuggable; supports streaming natively.
**Trade-off:** More boilerplate than simple chain; worth it for production-grade agents.

### ADR-004: MCP as external interface layer
**Decision:** Expose RAG and agent capabilities as MCP tools.
**Reason:** Allows any MCP-compatible client (Claude Desktop, Cursor, etc.) to consume platform capabilities without API changes.
**Trade-off:** Additional server to maintain; standardized protocol reduces integration cost.

### ADR-005: RAGAS for evaluation
**Decision:** Use RAGAS metrics as quality gates in CI.
**Reason:** Standardized, LLM-based metrics for faithfulness, relevance, precision — correlate with human judgement.
**Trade-off:** Eval runs cost tokens; run only on PR to main, not every commit.

---

## Observability architecture

```
Application (OpenTelemetry SDK)
    │  traces + metrics
    ▼
OpenTelemetry Collector
    ├──► Jaeger  (traces)
    └──► Prometheus  (metrics)
              │
              ▼
         Grafana  (dashboards)
```

**Trace propagation:** every API request generates a `trace_id` that flows through RAG retrieval → LLM call → response. Logged in every JSON log line for correlation.

**Key metrics:**
- `llm_calls_total{model, status}` — counter
- `llm_latency_seconds{model}` — histogram (p50, p95, p99)
- `token_usage_total{model, type}` — counter (prompt / completion)
- `retrieval_latency_seconds{store}` — histogram
- `retrieval_top_k_results{store}` — histogram

---

## Security layers

```
Request
  └─► [Rate Limiting]          nginx / API gateway
  └─► [TLS termination]        infra layer
  └─► [JWT Auth + RBAC]        src/security/rbac.py
  └─► [Prompt Shield]          src/security/prompt_shield.py
  └─► [Input Guardrails]       src/security/guardrails.py
  └─► [LLM Call]               src/core/llm_client.py
  └─► [Output Guardrails]      src/security/guardrails.py
  └─► Response
```

**RBAC roles:**
- `viewer` — read-only: query, list documents
- `editor` — viewer + index documents, run agents
- `admin` — editor + manage users, view metrics

---

## Azure production architecture (Phase 9)

```
Azure Virtual Network (private)
  ├── Azure Container Apps  ──── API service (private endpoint)
  ├── Azure OpenAI           ──── private endpoint
  ├── Azure AI Search        ──── private endpoint
  ├── Azure Container Registry
  └── Azure Monitor / Application Insights

Auth: Managed Identity (no stored credentials)
Secrets: Azure Key Vault
```
