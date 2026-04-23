"""
config_loader.py — Reads client and module JSON config files.
"""

import json
from pathlib import Path
from typing import Dict, Any
from app.core.types import ClientConfig, ModuleConfig


CONFIG_DIR = Path(__file__).parent.parent.parent / "config"


def load_client(client_id: str) -> ClientConfig:
    """Load a client config by client_id."""
    path = CONFIG_DIR / "clients" / f"{client_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Client config not found: {path}")
    with open(path) as f:
        data = json.load(f)
    return ClientConfig(data)


def load_module_config(module_name: str) -> ModuleConfig:
    """Load a module config by module name."""
    path = CONFIG_DIR / "modules" / f"{module_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Module config not found: {path}")
    with open(path) as f:
        data = json.load(f)
    return ModuleConfig(data)
