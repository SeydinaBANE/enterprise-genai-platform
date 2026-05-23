from __future__ import annotations

from src.observability.logging import get_logger

logger = get_logger(__name__)

_BLOCKED_TOPICS = [
    "bomb",
    "weapon",
    "malware",
    "exploit",
    "hack into",
    "steal credentials",
]


class ContentGuardrail:
    """Lightweight keyword-based guardrail.

    Replace or extend with guardrails-ai validators or Azure Content Safety
    when AZURE_CONTENT_SAFETY_ENDPOINT is configured.
    """

    async def validate_input(self, text: str) -> tuple[bool, str]:
        lower = text.lower()
        for topic in _BLOCKED_TOPICS:
            if topic in lower:
                logger.warning("input_blocked", topic=topic)
                return False, f"Input contains blocked content related to: {topic}"
        return True, ""

    async def validate_output(self, text: str) -> tuple[bool, str]:
        lower = text.lower()
        for topic in _BLOCKED_TOPICS:
            if topic in lower:
                logger.warning("output_blocked", topic=topic)
                return False, "Generated response contains blocked content."
        return True, ""
