"""
logger.py — Creates safe structured execution log events.

Records operational facts without recording sensitive content.
All events pass through the redactor before being returned.
"""

from typing import Any, Dict
from app.core.redactor import redact_dict


def build_log_event(
    event_type: str,
    context_dict: Dict[str, Any],
    output_valid: bool,
) -> Dict[str, Any]:
    """
    Build a safe structured log event from execution context.

    What belongs in a log event:
    - event type
    - client_id (not client name — just the ID)
    - module name and version
    - data sources used (names only, not content)
    - whether output was valid

    What never belongs in a log event:
    - raw prompt text
    - raw LLM response
    - user personal data
    - PII of any kind
    """
    raw_event = {
        "event_type": event_type,
        "client_id": context_dict.get("client_id", ""),
        "module_name": context_dict.get("module_name", ""),
        "module_version": context_dict.get("module_version", ""),
        "user_request": context_dict.get("user_request", ""),  # will be redacted
        "data_sources": ", ".join(context_dict.get("data_sources", [])),
        "output_valid": str(output_valid),
    }
    return redact_dict(raw_event)
