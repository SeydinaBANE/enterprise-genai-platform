from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.core.config import settings

_tracer: trace.Tracer | None = None


def configure_tracing() -> None:
    global _tracer
    resource = Resource.create({"service.name": settings.otel_service_name})
    provider = TracerProvider(resource=resource)

    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    _tracer = trace.get_tracer(settings.otel_service_name)


def get_tracer() -> trace.Tracer:
    if _tracer is None:
        return trace.get_tracer(settings.otel_service_name)
    return _tracer


def traced(span_name: str) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            tracer = get_tracer()
            with tracer.start_as_current_span(span_name) as span:
                span.set_attribute("function", func.__qualname__)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.StatusCode.OK)
                    return result
                except Exception as exc:
                    span.set_status(trace.StatusCode.ERROR, str(exc))
                    span.record_exception(exc)
                    raise

        return wrapper

    return decorator
