from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .config_loader import REPO_ROOT
from .enterprise_api import validate_api_access
from .policy_engine import evaluate_request
from .token_broker import exchange_token_from_decision

DEFAULT_EVIDENCE_RUNS_DIR = REPO_ROOT / "evidence" / "runs"


def load_request(request_path: str | Path) -> dict[str, Any]:
    """Load a JSON sample request from disk."""
    path = Path(request_path)
    with path.open("r", encoding="utf-8") as handle:
        request = json.load(handle)
    if not isinstance(request, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return request


def _safe_filename(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)
    return "-".join(part for part in safe.split("-") if part) or "request"


def _utc_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _write_evidence(evidence: dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    request_id = _safe_filename(str(evidence.get("request_id", "request")))
    demo_run_id = _safe_filename(str(evidence.get("demo_run_id", "run")))
    output_path = output_dir / f"{request_id}-{demo_run_id}.json"
    output_path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return output_path


def run_demo_request(
    request: dict[str, Any],
    *,
    output_dir: str | Path = DEFAULT_EVIDENCE_RUNS_DIR,
    now_epoch: int | None = None,
    write_output: bool = True,
) -> tuple[dict[str, Any], Path | None]:
    """Run the local end-to-end brokered delegation demo.

    Flow:

    request -> policy decision -> token broker -> enterprise API validation -> evidence JSON

    The runner intentionally writes token metadata only. It never writes raw bearer
    token material into evidence.
    """
    decision = evaluate_request(request)
    token_result = exchange_token_from_decision(decision, now_epoch=now_epoch)

    evidence = decision.to_evidence()
    evidence.update(
        {
            "demo_phase": "phase_4a_local_demo_runner",
            "demo_run_id": str(uuid4()),
            "demo_generated_at": _utc_timestamp(),
            "token_exchange": token_result.token_exchange,
            "token_exchange_reason_code": token_result.reason_code,
            "raw_token_logged": False,
        }
    )

    token_update = token_result.to_evidence_update()
    for key in ["token_audience", "token_scope", "token_ttl_seconds", "token_jti"]:
        if key in token_update:
            evidence[key] = token_update[key]

    if token_result.delegated_token is None:
        evidence.update(
            {
                "api_access": "NOT_ATTEMPTED",
                "api_authorization_decision": "NOT_ATTEMPTED",
                "api_reason_code": "TOKEN_NOT_ISSUED",
            }
        )
    else:
        api_result = validate_api_access(
            token_result.delegated_token,
            target_app=str(request.get("target_app")),
            required_scope=str(request.get("requested_scope")),
            now_epoch=now_epoch,
        )
        api_update = api_result.to_evidence_update()
        evidence.update(
            {
                "api_access": "SUCCESS" if api_result.api_access == "ALLOW" else "FAILED",
                "api_authorization_decision": api_result.api_access,
                "api_reason_code": api_result.reason_code,
                "api_target_app": api_result.target_app,
                "api_required_scope": api_result.required_scope,
                "api_token_expired": api_result.token_expired,
                "raw_token_logged": False,
            }
        )
        for key in ["token_subject", "token_actor", "token_audience", "token_scope"]:
            if key in api_update:
                evidence[f"api_{key}"] = api_update[key]

    output_path = None
    if write_output:
        output_path = _write_evidence(evidence, Path(output_dir))

    return evidence, output_path


def run_demo_file(
    request_path: str | Path,
    *,
    output_dir: str | Path = DEFAULT_EVIDENCE_RUNS_DIR,
    now_epoch: int | None = None,
) -> tuple[dict[str, Any], Path]:
    """Run the demo from a JSON request file and write evidence to disk."""
    request = load_request(request_path)
    evidence, output_path = run_demo_request(
        request,
        output_dir=output_dir,
        now_epoch=now_epoch,
        write_output=True,
    )
    if output_path is None:
        raise RuntimeError("Expected evidence output path to be written")
    return evidence, output_path
