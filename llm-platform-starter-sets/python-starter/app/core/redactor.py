"""
redactor.py — Masks sensitive values before logging.

Logs are not private. Treat every log line as potentially visible.
Redact emails, phone numbers, and other PII before any log sink sees them.
"""

import re
from typing import Any, Dict


# Patterns to redact
EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)
PHONE_PATTERN = re.compile(
    r"\b(?:\+1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}\b"
)


def redact_text(value: str) -> str:
    """Redact known PII patterns from a text string."""
    value = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
    value = PHONE_PATTERN.sub("[REDACTED_PHONE]", value)
    return value


def redact_dict(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact string fields in a dictionary (one level deep).
    Non-string values are passed through unchanged.
    """
    redacted = {}
    for key, value in data.items():
        if isinstance(value, str):
            redacted[key] = redact_text(value)
        else:
            redacted[key] = value
    return redacted
