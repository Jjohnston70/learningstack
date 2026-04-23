"""
types.py — Shared data structures for the modular LLM platform.

These types define the contracts between layers:
- ClientConfig: what we know about a client
- ModuleConfig: what a module is and what it does
- ExecutionRequest: what came in from the user
- ExecutionContext: what the runtime assembled to process the request
- ExecutionResult: what came back from the module
"""

from typing import Any, Dict, List, Optional


class ClientConfig:
    """Represents a loaded client configuration."""

    def __init__(self, data: Dict[str, Any]):
        self.client_id: str = data["client_id"]
        self.name: str = data["name"]
        self.active_modules: List[str] = data.get("active_modules", [])
        self.module_versions: Dict[str, str] = data.get("module_versions", {})
        self.branding: Dict[str, str] = data.get("branding", {})
        self.data_sources: List[str] = data.get("data_sources", [])
        self.permissions: Dict[str, List[str]] = data.get("permissions", {})
        self.model_preferences: Dict[str, str] = data.get("model_preferences", {})

    @property
    def tone(self) -> str:
        return self.branding.get("tone", "clear and professional")

    def can_use_module(self, module_name: str) -> bool:
        return module_name in self.active_modules

    def get_permissions(self, module_name: str) -> List[str]:
        return self.permissions.get(module_name, [])


class ModuleConfig:
    """Represents a loaded module configuration."""

    def __init__(self, data: Dict[str, Any]):
        self.name: str = data["name"]
        self.version: str = data.get("version", "1.0.0")
        self.description: str = data.get("description", "")
        self.required_tools: List[str] = data.get("required_tools", [])
        self.required_permissions: List[str] = data.get("required_permissions", [])
        self.output_mode: str = data.get("output_mode", "freeform")
        self.output_fields: List[str] = data.get("output_fields", [])
        self.keywords: List[str] = data.get("keywords", [])


class ExecutionRequest:
    """Represents an incoming user request."""

    def __init__(self, client_id: str, user_input: str, metadata: Optional[Dict] = None):
        self.client_id = client_id
        self.user_input = user_input
        self.metadata = metadata or {}


class ExecutionContext:
    """
    The canonical context object passed through the execution pipeline.
    Built by context_builder from client config + module config + user request.
    """

    def __init__(
        self,
        client_id: str,
        client_name: str,
        tone: str,
        module_name: str,
        module_version: str,
        user_request: str,
        data_sources: List[str],
        permissions: List[str],
        output_fields: List[str],
    ):
        self.client_id = client_id
        self.client_name = client_name
        self.tone = tone
        self.module_name = module_name
        self.module_version = module_version
        self.user_request = user_request
        self.data_sources = data_sources
        self.permissions = permissions
        self.output_fields = output_fields

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "client_name": self.client_name,
            "tone": self.tone,
            "module_name": self.module_name,
            "module_version": self.module_version,
            "user_request": self.user_request,
            "data_sources": self.data_sources,
            "permissions": self.permissions,
            "output_fields": self.output_fields,
        }


class ExecutionResult:
    """Represents the result of a module execution."""

    def __init__(
        self,
        success: bool,
        output: Optional[Dict[str, Any]] = None,
        errors: Optional[List[str]] = None,
        module_name: str = "",
    ):
        self.success = success
        self.output = output or {}
        self.errors = errors or []
        self.module_name = module_name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "output": self.output,
            "errors": self.errors,
            "module_name": self.module_name,
        }
