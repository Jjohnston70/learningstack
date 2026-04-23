"""
proposal_tools.py — Tool adapters for proposal generation workflows.

Bridge between LLM runtime and Google Docs/Drive/Forms/Sheets.
"""

import os
from typing import Any, Dict, List


def build_proposal_document(
    client_name: str,
    deliverables: List[str],
    timeline: str,
    template_id: str = "",
) -> Dict[str, Any]:
    """
    Generate a proposal Google Doc from a template.

    Phase 5+: POST to Apps Script web app with template_id and content.
    Real implementation calls proposal-generator.js via deployed web app URL.
    """
    print(f"[STUB] build_proposal_document — client={client_name}")
    return {
        "document_url": "",
        "document_id": "",
        "note": "[STUB] Real document generation not yet connected"
    }


def log_proposal_to_tracker(
    client_name: str,
    proposal_summary: str,
    spreadsheet_id: str = "",
) -> Dict[str, Any]:
    """
    Log a proposal entry to the tracking spreadsheet.

    Phase 5+: POST to Apps Script web app or use Sheets API.
    """
    print(f"[STUB] log_proposal_to_tracker — client={client_name}")
    return {
        "row_added": False,
        "note": "[STUB] Real tracking log not yet connected"
    }


def send_proposal_email(
    recipient_email: str,
    proposal_url: str,
    client_name: str,
) -> Dict[str, Any]:
    """
    Send proposal email with document link.

    Phase 5+: Call Gmail API or Apps Script email function.
    NOTE: Requires explicit permission check before sending.
    """
    print(f"[STUB] send_proposal_email — recipient redacted for stub")
    return {
        "sent": False,
        "note": "[STUB] Real email send not yet connected"
    }
