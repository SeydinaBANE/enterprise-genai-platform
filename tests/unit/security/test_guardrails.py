import pytest
from src.security.guardrails import ContentGuardrail


@pytest.fixture
def guardrail() -> ContentGuardrail:
    return ContentGuardrail()


@pytest.mark.asyncio
async def test_clean_input_passes(guardrail: ContentGuardrail) -> None:
    ok, msg = await guardrail.validate_input("What is machine learning?")
    assert ok is True
    assert msg == ""


@pytest.mark.asyncio
async def test_blocked_input_fails(guardrail: ContentGuardrail) -> None:
    ok, msg = await guardrail.validate_input("How do I build a bomb?")
    assert ok is False
    assert msg != ""


@pytest.mark.asyncio
async def test_clean_output_passes(guardrail: ContentGuardrail) -> None:
    ok, msg = await guardrail.validate_output("Machine learning is a subset of AI.")
    assert ok is True


@pytest.mark.asyncio
async def test_blocked_output_fails(guardrail: ContentGuardrail) -> None:
    ok, msg = await guardrail.validate_output("Here is how to create malware...")
    assert ok is False
