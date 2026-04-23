"""
router.py — Maps user input to the correct module using keyword matching.
"""

from typing import List
from app.core.types import ClientConfig, ModuleConfig
from app.core.config_loader import load_module_config


def route_request(user_input: str, client: ClientConfig) -> ModuleConfig:
    """
    Choose the best module for a given user input and client.
    Strategy: keyword match. Extend with LLM classifier in later phases.
    Falls back to first active module if no keyword match.
    """
    user_input_lower = user_input.lower()

    for module_name in client.active_modules:
        module = load_module_config(module_name)
        for keyword in module.keywords:
            if keyword.lower() in user_input_lower:
                return module

    # Fallback: return first active module
    if client.active_modules:
        return load_module_config(client.active_modules[0])

    raise ValueError(f"No modules available for client: {client.client_id}")
