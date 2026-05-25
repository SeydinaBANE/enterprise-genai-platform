from __future__ import annotations

from src.observability.metrics import (
    llm_calls_total,
    llm_latency_seconds,
    retrieval_latency_seconds,
    retrieval_results_count,
    token_usage_total,
)


def test_all_metrics_importable() -> None:
    assert llm_calls_total is not None
    assert llm_latency_seconds is not None
    assert retrieval_latency_seconds is not None
    assert retrieval_results_count is not None
    assert token_usage_total is not None


def test_counter_increments() -> None:
    before = llm_calls_total.labels(model="test-model", status="ok")._value.get()
    llm_calls_total.labels(model="test-model", status="ok").inc()
    after = llm_calls_total.labels(model="test-model", status="ok")._value.get()
    assert after == before + 1


def test_histogram_observable() -> None:
    llm_latency_seconds.labels(model="test-model").observe(0.5)
    retrieval_latency_seconds.labels(store="chroma").observe(0.1)
    retrieval_results_count.labels(store="chroma").observe(3)
