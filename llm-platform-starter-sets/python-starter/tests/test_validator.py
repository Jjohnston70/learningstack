"""
test_validator.py — Tests for the output validation utility.

Run: python -m pytest tests/test_validator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.validator import validate_output


class TestValidateOutput:

    def test_valid_output_passes(self):
        output = {
            "summary": "Three invoices are overdue.",
            "risks": ["Cash flow pressure increasing"],
            "recommended_actions": ["Follow up with top debtor today"]
        }
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is True
        assert errors == []

    def test_missing_field_fails(self):
        output = {"summary": "Some summary"}
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is False
        assert any("risks" in e for e in errors)
        assert any("recommended_actions" in e for e in errors)

    def test_null_field_fails(self):
        output = {"summary": None, "risks": ["Risk 1"], "recommended_actions": ["Action 1"]}
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is False
        assert any("null" in e for e in errors)

    def test_empty_string_fails(self):
        output = {"summary": "   ", "risks": ["Risk 1"], "recommended_actions": ["Action 1"]}
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is False

    def test_empty_list_fails(self):
        output = {"summary": "Summary here", "risks": [], "recommended_actions": ["Action 1"]}
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is False
        assert any("risks" in e for e in errors)

    def test_no_required_fields_always_passes(self):
        output = {"anything": "goes here"}
        is_valid, errors = validate_output(output, [])
        assert is_valid is True

    def test_extra_fields_are_ignored(self):
        output = {
            "summary": "Summary",
            "risks": ["Risk"],
            "recommended_actions": ["Action"],
            "extra_field": "This is fine"
        }
        is_valid, errors = validate_output(output, ["summary", "risks", "recommended_actions"])
        assert is_valid is True
