from __future__ import annotations

from src.observability.logging import configure_logging, get_logger


def test_get_logger_not_none() -> None:
    logger = get_logger("test.module")
    assert logger is not None


def test_configure_logging_runs() -> None:
    configure_logging()


def test_configure_logging_idempotent() -> None:
    configure_logging()
    configure_logging()
