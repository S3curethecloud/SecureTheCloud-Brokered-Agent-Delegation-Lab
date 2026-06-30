from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .demo_runner import DEFAULT_EVIDENCE_RUNS_DIR

SUMMARY_FIELDS = [
    ("Request", "request_id"),
    ("Policy", "policy_decision"),
    ("Token Exchange", "token_exchange"),
    ("API Decision", "api_authorization_decision"),
    ("API Access", "api_access"),
    ("User", "user"),
    ("Agent", "agent"),
    ("Target App", "target_app"),
    ("Scope", "requested_scope"),
    ("Token Audience", "token_audience"),
    ("API Reason", "api_reason_code"),
    ("Raw Token Logged", "raw_token_logged"),
]


def list_evidence_files(evidence_dir: str | Path = DEFAULT_EVIDENCE_RUNS_DIR) -> list[Path]:
    """Return generated evidence JSON files sorted by modification time."""
    path = Path(evidence_dir)
    if not path.exists():
        return []
    return sorted(
        (item for item in path.glob("*.json") if item.is_file()),
        key=lambda item: item.stat().st_mtime,
    )


def latest_evidence_file(evidence_dir: str | Path = DEFAULT_EVIDENCE_RUNS_DIR) -> Path:
    """Return the latest generated evidence JSON file."""
    files = list_evidence_files(evidence_dir)
    if not files:
        raise FileNotFoundError(f"No evidence JSON files found in {Path(evidence_dir)}")
    return files[-1]


def load_evidence(path: str | Path) -> dict[str, Any]:
    """Load an evidence JSON file."""
    evidence_path = Path(path)
    with evidence_path.open("r", encoding="utf-8") as handle:
        evidence = json.load(handle)
    if not isinstance(evidence, dict):
        raise ValueError(f"Expected JSON object in {evidence_path}")
    return evidence


def summarize_evidence(evidence: dict[str, Any]) -> str:
    """Create a clean human-readable evidence summary."""
    lines = ["SecureTheCloud Brokered Delegation Evidence Summary", "=" * 56]
    for label, key in SUMMARY_FIELDS:
        value = evidence.get(key, "N/A")
        if isinstance(value, bool):
            value = str(value).lower()
        lines.append(f"{label}: {value}")
    return "\n".join(lines)


def summarize_latest_evidence(evidence_dir: str | Path = DEFAULT_EVIDENCE_RUNS_DIR) -> tuple[Path, str]:
    """Load and summarize the latest evidence file."""
    path = latest_evidence_file(evidence_dir)
    evidence = load_evidence(path)
    return path, summarize_evidence(evidence)
