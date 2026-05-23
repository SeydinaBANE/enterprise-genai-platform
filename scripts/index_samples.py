"""Index sample documents for local development and testing."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.dependencies import get_indexing_pipeline
from src.core.models import Document
from src.observability.logging import configure_logging

SAMPLE_DOCS = [
    Document(
        title="GenAI Platform Overview",
        content="""
Enterprise GenAI Platform — Technical Overview

This platform provides production-grade generative AI capabilities including:

Retrieval-Augmented Generation (RAG)
RAG combines vector search with language generation to answer questions from documents.
The pipeline includes document loading, chunking, embedding, hybrid retrieval (semantic + BM25),
reranking, and answer generation with source citations.

Multi-Agent Orchestration
LangGraph powers a supervisor-worker architecture where specialized agents collaborate:
- Researcher: gathers information from the knowledge base and web
- Analyst: processes and synthesizes findings
The supervisor routes tasks and merges outputs into coherent responses.

Model Context Protocol (MCP)
The platform exposes its capabilities as MCP tools, enabling any compatible client
(Claude Desktop, Cursor, etc.) to access RAG queries and agent runs programmatically.

Security Architecture
Security is enforced at every layer:
- RBAC: JWT-based roles (viewer, editor, admin) on all API routes
- Guardrails: content filtering on both input and output
- Prompt Shield: injection detection before reaching the LLM
- All secrets managed via environment variables

Observability
Every LLM call and retrieval operation is instrumented:
- OpenTelemetry traces exported to Jaeger
- Prometheus metrics: latency, token usage, error rates
- Structured JSON logs with trace correlation IDs
- Grafana dashboards for real-time monitoring
        """.strip(),
        source="sample_overview.txt",
    ),
    Document(
        title="Azure AI Services Guide",
        content="""
Azure AI Services for GenAI Workloads

Azure OpenAI Service
Provides access to GPT-4o, GPT-4, and embedding models through a managed, enterprise-grade API.
Key features: private endpoints, Managed Identity auth, content filtering built-in,
provisioned throughput for predictable performance.

Azure AI Search
Enterprise vector store supporting hybrid search (semantic + keyword).
Integrated with Azure OpenAI for vectorization. Supports RBAC, private networking,
and semantic ranking out of the box.

Azure Container Apps
Serverless container hosting for the API service. Scales to zero, supports Dapr sidecars,
Managed Identity for secrets-free deployment.

Microsoft Foundry (Azure AI Foundry)
Unified platform for deploying and managing AI models. Provides model catalog,
fine-tuning, evaluation, and responsible AI tooling.

Managed Identity Pattern
Best practice: assign a user-assigned Managed Identity to the Container App.
Grant it roles: Cognitive Services OpenAI User, Search Index Data Reader.
No API keys stored — authentication is token-based via Azure AD.

Network Security
Deploy all services in a private VNet. Use Private Endpoints for Azure OpenAI and AI Search.
Route all traffic through Azure Firewall. Disable public access.
        """.strip(),
        source="azure_guide.txt",
    ),
]


async def main() -> None:
    configure_logging()
    pipeline = get_indexing_pipeline()

    for doc in SAMPLE_DOCS:
        print(f"Indexing: {doc.title}...")
        chunks = await pipeline.index(doc)
        print(f"  → {len(chunks)} chunks indexed")

    print("\n✅ Sample documents indexed. Run `make run` and test with:")
    print('  curl -X POST http://localhost:8000/query \\')
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"question": "What is RAG?"}\'')


if __name__ == "__main__":
    asyncio.run(main())
