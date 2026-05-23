from __future__ import annotations

import re

from src.observability.logging import get_logger

logger = get_logger(__name__)

_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"disregard\s+(all\s+)?previous\s+instructions",
    r"forget\s+(all\s+)?previous\s+instructions",
    r"you\s+are\s+now\s+(?!an?\s+assistant)",
    r"act\s+as\s+(?:dan|jailbreak|unrestricted)",
    r"<\s*system\s*>",
    r"\[system\]",
    r"##\s*new\s+instructions",
    r"override\s+system\s+prompt",
]

_COMPILED = [re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS]


def detect_injection(text: str) -> tuple[bool, str]:
    for pattern in _COMPILED:
        if pattern.search(text):
            logger.warning("prompt_injection_detected", pattern=pattern.pattern[:40])
            return True, "Potential prompt injection detected."
    return False, ""
