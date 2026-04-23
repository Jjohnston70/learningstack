"""
test_redactor.py — Tests for the redaction utility.

Run: python -m pytest tests/test_redactor.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.redactor import redact_text, redact_dict


class TestRedactText:

    def test_email_is_redacted(self):
        result = redact_text("Contact us at jacob@truenorthstrategyops.com for details.")
        assert "[REDACTED_EMAIL]" in result
        assert "jacob@truenorthstrategyops.com" not in result

    def test_phone_is_redacted(self):
        result = redact_text("Call us at 719-204-6365 today.")
        assert "[REDACTED_PHONE]" in result
        assert "719-204-6365" not in result

    def test_phone_with_parens_is_redacted(self):
        result = redact_text("Reach us at (719) 204-6365.")
        assert "[REDACTED_PHONE]" in result

    def test_clean_text_passes_through(self):
        text = "The invoice total is $1,200 for the Command Center Build."
        result = redact_text(text)
        assert result == text

    def test_multiple_emails_redacted(self):
        text = "Send to alice@example.com and bob@company.org"
        result = redact_text(text)
        assert result.count("[REDACTED_EMAIL]") == 2

    def test_empty_string(self):
        assert redact_text("") == ""


class TestRedactDict:

    def test_email_in_dict_value_is_redacted(self):
        data = {"user_request": "Email me at jacob@truenorthstrategyops.com", "client_id": "client-alpha"}
        result = redact_dict(data)
        assert "[REDACTED_EMAIL]" in result["user_request"]
        assert result["client_id"] == "client-alpha"  # unchanged

    def test_non_string_values_pass_through(self):
        data = {"count": 42, "flags": [True, False], "score": 3.14}
        result = redact_dict(data)
        assert result["count"] == 42
        assert result["flags"] == [True, False]
        assert result["score"] == 3.14

    def test_empty_dict(self):
        assert redact_dict({}) == {}
