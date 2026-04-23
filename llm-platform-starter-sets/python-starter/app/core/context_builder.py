"""
context_builder.py — Builds the structured execution context object.
"""

from app.core.types import ClientConfig, ModuleConfig, ExecutionContext


def build_context(
    client: ClientConfig,
    module: ModuleConfig,
    user_request: str,
) -> ExecutionContext:
    """
    Create a structured ExecutionContext from client config, module config, and user request.
    This is the canonical object passed through all runtime layers.
    """
    return ExecutionContext(
        client_id=client.client_id,
        client_name=client.name,
        tone=client.tone,
        module_name=module.name,
        module_version=module.version,
        user_request=user_request,
        data_sources=client.data_sources,
        permissions=client.get_permissions(module.name),
        output_fields=module.output_fields,
    )
