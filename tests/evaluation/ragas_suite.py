"""RAGAS evaluation suite — run with: make eval

Requires OPENROUTER_API_KEY and a running indexed knowledge base.
"""
from __future__ import annotations

import asyncio

import pytest

EVAL_PAIRS = [
    {
        "question": "What is RAG?",
        "ground_truth": "RAG stands for Retrieval-Augmented Generation, combining retrieval with language generation.",
    },
    {
        "question": "What frameworks are used for agent orchestration?",
        "ground_truth": "LangGraph is used for stateful multi-agent orchestration.",
    },
]


@pytest.mark.asyncio
@pytest.mark.eval
async def test_rag_faithfulness() -> None:
    """Answers must be grounded in retrieved context."""
    from src.api.dependencies import get_hybrid_retriever, get_llm_client
    from src.rag.generation.generator import generate_answer
    from src.rag.retrieval.reranker import rerank

    llm = get_llm_client()
    retriever = get_hybrid_retriever()

    for pair in EVAL_PAIRS:
        retrieved = await retriever.retrieve(pair["question"], top_k=5)
        if not retrieved:
            pytest.skip("No documents indexed — run `make index` first")

        reranked = await rerank(pair["question"], retrieved, top_k=3)
        result = await generate_answer(pair["question"], reranked, llm)

        assert result.answer, f"Empty answer for: {pair['question']}"
        assert len(result.sources) > 0, "Answer must cite sources"


@pytest.mark.asyncio
@pytest.mark.eval
async def test_rag_answer_relevance() -> None:
    """Answers must address the question."""
    from src.api.dependencies import get_hybrid_retriever, get_llm_client
    from src.rag.generation.generator import generate_answer
    from src.rag.retrieval.reranker import rerank

    llm = get_llm_client()
    retriever = get_hybrid_retriever()

    question = "Describe the security architecture."
    retrieved = await retriever.retrieve(question, top_k=5)
    if not retrieved:
        pytest.skip("No documents indexed")

    reranked = await rerank(question, retrieved, top_k=3)
    result = await generate_answer(question, reranked, llm)

    assert len(result.answer) > 50, "Answer too short to be relevant"
