"""
financial_tools.py — Tool adapters for financial analysis operations.

Bridge between LLM runtime and Google Sheets financial data.
"""

from typing import Any, Dict, List


def get_invoice_summary(spreadsheet_id: str = "", sheet_name: str = "Invoices") -> Dict[str, Any]:
    """
    Retrieve overdue and pending invoice data from a tracking spreadsheet.

    Phase 5+: Use Sheets API or Apps Script web app to read invoice tab.
    """
    print(f"[STUB] get_invoice_summary — sheet={sheet_name}")
    return {
        "overdue_count": 0,
        "overdue_amount": 0.0,
        "pending_count": 0,
        "pending_amount": 0.0,
        "invoices": [],
        "note": "[STUB] Real Sheets read not yet connected"
    }


def get_cashflow_data(
    spreadsheet_id: str = "",
    weeks_ahead: int = 4,
) -> Dict[str, Any]:
    """
    Retrieve cash flow projection data.

    Phase 5+: Read from financial model tab in Sheets.
    """
    print(f"[STUB] get_cashflow_data — weeks_ahead={weeks_ahead}")
    return {
        "inflow_projected": 0.0,
        "outflow_projected": 0.0,
        "net_position": 0.0,
        "weeks": [],
        "note": "[STUB] Real cash flow data not yet connected"
    }


def calculate_margin(revenue: float, costs: float) -> Dict[str, Any]:
    """
    Calculate gross margin. Safe to run without external calls.
    """
    if revenue == 0:
        return {"gross_margin": 0.0, "margin_percent": 0.0}
    gross_margin = revenue - costs
    margin_percent = (gross_margin / revenue) * 100
    return {
        "gross_margin": round(gross_margin, 2),
        "margin_percent": round(margin_percent, 2)
    }
