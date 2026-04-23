"""
test_module.py — Starter tests for [your-module-name].

These tests verify:
- The module wrapper imports and runs without error
- Output matches the required schema fields
- Permission checks work as expected
- Tool stubs are wired (stubs return placeholder data)

Run: python -m pytest module-template/tests/test_module.py -v
"""

import sys
import os

# Adjust import path when running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import the module adapter
from module_template.adapters.python.module import run, error_response


SAMPLE_CONTEXT = {
    "client_id": "client-alpha",
    "client_name": "Client Alpha",
    "tone": "direct, practical",
    "module_name": "your-module-name",
    "module_version": "1.0.0",
    "user_request": "Test request for the module",
    "data_sources": ["alpha-drive", "alpha-sheets"],
    "permissions": ["read"],
    "output_fields": ["summary", "risks", "recommended_actions"],
}


class TestModuleRun:

    def test_module_runs_without_error(self):
        result = run(SAMPLE_CONTEXT)
        assert isinstance(result, dict)

    def test_output_has_required_fields(self):
        result = run(SAMPLE_CONTEXT)
        assert "summary" in result
        assert "risks" in result
        assert "recommended_actions" in result

    def test_summary_is_non_empty_string(self):
        result = run(SAMPLE_CONTEXT)
        assert isinstance(result["summary"], str)
        assert len(result["summary"].strip()) > 0

    def test_risks_is_non_empty_list(self):
        result = run(SAMPLE_CONTEXT)
        assert isinstance(result["risks"], list)
        assert len(result["risks"]) > 0

    def test_recommended_actions_is_non_empty_list(self):
        result = run(SAMPLE_CONTEXT)
        assert isinstance(result["recommended_actions"], list)
        assert len(result["recommended_actions"]) > 0


class TestErrorResponse:

    def test_error_response_has_required_fields(self):
        result = error_response("Test error message")
        assert "summary" in result
        assert "risks" in result
        assert "recommended_actions" in result

    def test_error_summary_includes_message(self):
        result = error_response("Something went wrong")
        assert "Something went wrong" in result["summary"]
