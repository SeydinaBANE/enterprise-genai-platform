from __future__ import annotations

import pytest

from src.observability.tracing import configure_tracing, get_tracer, traced


async def test_traced_success() -> None:
    @traced("test.span")
    async def my_func(x: int) -> int:
        return x * 2

    assert await my_func(5) == 10


async def test_traced_propagates_exception() -> None:
    @traced("test.span")
    async def failing() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        await failing()


def test_get_tracer_returns_tracer() -> None:
    assert get_tracer() is not None


def test_configure_tracing_runs_without_error() -> None:
    configure_tracing()  # OTel exporter connects lazily; safe to call in tests
