from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping in {path}")
    return data


def load_config(config_dir: Path = CONFIG_DIR) -> dict[str, Any]:
    """Load lab configuration from YAML files."""
    return {
        "agents": load_yaml(config_dir / "agents.yaml").get("agents", []),
        "apps": load_yaml(config_dir / "apps.yaml").get("apps", []),
        "users": load_yaml(config_dir / "users.yaml").get("users", []),
        "scopes": load_yaml(config_dir / "scopes.yaml").get("scopes", []),
    }
