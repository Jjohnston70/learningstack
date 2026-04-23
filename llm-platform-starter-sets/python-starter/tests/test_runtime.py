"""
test_runtime.py — Integration test for the full request execution pipeline.

Run: python -m pytest tests/test_runtime.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.types import ExecutionRequest
from app.core.runtime import execute_request
from app.core.config_loader import load_client, load_module_config
from app.core.router import route_request
from app.core.context_builder import build_context
from app.core.redactor import redact_dict
from app.core.validator import validate_output


class TestConfigLoading:

    def test_client_alpha_loads(self):
        client = load_client("client-alpha")
        assert client.client_id == "client-alpha"
        assert "financial-command" in client.active_modules

    def test_financial_module_loads(self):
        module = load_module_config("financial-command")
        assert module.name == "financial-command"
        assert len(module.output_fields) > 0

    def test_missing_client_raises(self):
        try:
            load_client("does-not-exist")
            assert False, "Should have raised"
        except FileNotFoundError:
            pass


class TestRouting:

    def test_financial_keyword_routes_correctly(self):
        client = load_client("client-alpha")
        module = route_request("Show me overdue invoices and cash flow risk", client)
        assert module.name == "financial-command"

    def test_proposal_keyword_routes_correctly(self):
        client = load_client("client-alpha")
        module = route_request("Generate a proposal for the Command Center Build", client)
        assert module.name == "proposal-command"

    def test_fallback_returns_first_module(self):
        client = load_client("client-alpha")
        module = route_request("something completely unrelated", client)
        assert module.name in client.active_modules


class TestContextBuilder:

    def test_context_has_required_fields(self):
        client = load_client("client-alpha")
        module = load_module_config("financial-command")
        context = build_context(client, module, "Test request")
        assert context.client_id == "client-alpha"
        assert context.module_name == "financial-command"
        assert isinstance(context.data_sources, list)
        assert isinstance(context.output_fields, list)


class TestFullPipeline:

    def test_full_request_returns_result(self):
        request = ExecutionRequest(
            client_id="client-alpha",
            user_input="Summarize overdue invoices and cash flow risk."
        )
        result = execute_request(request)
        # Stub runtime returns data — should be valid or have known stub fields
        assert result.module_name == "financial-command"
        assert isinstance(result.output, dict)
        assert isinstance(result.success, bool)
