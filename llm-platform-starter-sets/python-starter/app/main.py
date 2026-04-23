"""
main.py — Local runner for testing the platform starter.

Run: python app/main.py
"""

from app.core.types import ExecutionRequest
from app.core.runtime import execute_request


def main():
    print("=== Modular LLM Platform Starter ===\n")

    # Example request — financial analysis
    request = ExecutionRequest(
        client_id="client-alpha",
        user_input="Summarize overdue invoices and identify top cash flow risks.",
    )

    print(f"Client: {request.client_id}")
    print(f"Request: {request.user_input}\n")

    result = execute_request(request)

    print("\n=== Result ===")
    print(f"Module: {result.module_name}")
    print(f"Success: {result.success}")
    if result.errors:
        print(f"Errors: {result.errors}")
    print(f"Output: {result.output}")


if __name__ == "__main__":
    main()
