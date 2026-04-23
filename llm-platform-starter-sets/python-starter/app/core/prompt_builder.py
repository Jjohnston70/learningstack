"""
prompt_builder.py — Assembles the final prompt from structured inputs.

This replaces copy-pasted prompt soup with a deterministic assembly process.
Inputs come from: client config + module instructions + user request.
"""

from pathlib import Path
from typing import List


MODULES_DIR = Path(__file__).parent.parent / "modules"


def load_module_instructions(module_name: str) -> str:
    """Load the instructions.md file for a module."""
    path = MODULES_DIR / module_name.replace("-", "_") / "instructions.md"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"(No instructions file found for module: {module_name})"


def build_prompt(
    client_name: str,
    tone: str,
    module_name: str,
    module_instructions: str,
    user_request: str,
    data_sources: List[str],
    output_fields: List[str],
) -> str:
    """
    Build the final prompt string sent to the LLM.

    This function is intentionally simple and readable.
    Later phases can replace this with templating or provider-specific formats.
    """
    data_source_text = ", ".join(data_sources) if data_sources else "none provided"
    output_field_text = ", ".join(output_fields) if output_fields else "freeform response"

    return f"""You are operating for client: {client_name}.
Response tone: {tone}.
Selected module: {module_name}.

Module instructions:
{module_instructions}

Approved data sources for this request:
{data_source_text}

User request:
{user_request}

Required output fields:
{output_field_text}

Rules:
- Do not invent facts not present in the provided context.
- Clearly label any assumptions.
- Return a concise, structured response matching the required output fields.
""".strip()
