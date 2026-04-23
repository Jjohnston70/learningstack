"""
validator.py — Validates that module output matches the expected schema.

"The model said something plausible" != "The system produced a valid output."
This module closes that gap.
"""

from typing import Any, Dict, List, Tuple


def validate_output(
    output: Dict[str, Any],
    required_fields: List[str],
) -> Tuple[bool, List[str]]:
    """
    Check that all required fields exist and are non-empty.
    Returns (is_valid, list_of_errors).
    """
    errors: List[str] = []

    for field in required_fields:
        if field not in output:
            errors.append(f"Missing required field: {field}")
            continue

        value = output[field]
        if value is None:
            errors.append(f"Field is null: {field}")
        elif isinstance(value, str) and not value.strip():
            errors.append(f"Field is empty string: {field}")
        elif isinstance(value, list) and len(value) == 0:
            errors.append(f"Field is empty list: {field}")

    return (len(errors) == 0, errors)
