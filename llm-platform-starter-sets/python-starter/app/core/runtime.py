"""
runtime.py — Main orchestration engine.

This is the foreman. It coordinates:
  load config → route → build context → build prompt → call module → validate → log → return
"""

from typing import Dict, Any
from app.core.types import ExecutionRequest, ExecutionResult
from app.core.config_loader import load_client, load_module_config
from app.core.router import route_request
from app.core.context_builder import build_context
from app.core.prompt_builder import build_prompt, load_module_instructions
from app.core.validator import validate_output
from app.core.logger import build_log_event


def execute_request(request: ExecutionRequest) -> ExecutionResult:
    """
    Full request execution pipeline.

    Steps:
    1. Load client config
    2. Route request to the right module
    3. Build execution context
    4. Load module instructions
    5. Build final prompt
    6. Execute module (Phase 7: replace stub with real LLM call)
    7. Validate output
    8. Log safely
    9. Return result
    """

    # Step 1 — Load client
    client = load_client(request.client_id)

    # Step 2 — Route to module
    module = route_request(request.user_input, client)

    # Step 3 — Build context
    context = build_context(client, module, request.user_input)

    # Step 4 — Load module instructions
    instructions = load_module_instructions(module.name)

    # Step 5 — Build final prompt
    prompt = build_prompt(
        client_name=context.client_name,
        tone=context.tone,
        module_name=context.module_name,
        module_instructions=instructions,
        user_request=context.user_request,
        data_sources=context.data_sources,
        output_fields=context.output_fields,
    )

    # Step 6 — Execute module
    # Phase 1/2: stub output. Phase 7: replace with real LLM call.
    output = _call_module_stub(module.name, prompt, context.to_dict())

    # Step 7 — Validate output
    is_valid, errors = validate_output(output, module.output_fields)

    # Step 8 — Log safely
    log_event = build_log_event(
        event_type="request_completed",
        context_dict=context.to_dict(),
        output_valid=is_valid,
    )
    _emit_log(log_event)

    # Step 9 — Return result
    return ExecutionResult(
        success=is_valid,
        output=output,
        errors=errors,
        module_name=module.name,
    )


def _call_module_stub(module_name: str, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Stub module executor. Replace this in Phase 7 with a real LLM call.

    In Phase 7:
        response = llm_provider.complete(prompt)
        return parse_structured_output(response)
    """
    print(f"\n[STUB] Would call LLM with module: {module_name}")
    print(f"[STUB] Prompt length: {len(prompt)} chars")
    print(f"[STUB] Client: {context.get('client_id')}")
    print(f"[STUB] Data sources: {context.get('data_sources')}")

    # Return a stub output matching common module output fields
    return {
        "summary": f"[STUB] Response from {module_name} for request: {context.get('user_request', '')[:50]}",
        "risks": ["[STUB] Risk item 1", "[STUB] Risk item 2"],
        "recommended_actions": ["[STUB] Action item 1"],
    }


def _emit_log(log_event: Dict[str, Any]) -> None:
    """
    Emit a log event. Replace with real logging in Phase 7/8.
    In production: send to Datadog, CloudWatch, etc.
    """
    print(f"\n[LOG] {log_event}")
