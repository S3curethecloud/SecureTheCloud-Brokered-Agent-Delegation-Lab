#!/usr/bin/env python
from __future__ import annotations

import argparse
import json
from pathlib import Path

from brokered_delegation.demo_runner import DEFAULT_EVIDENCE_RUNS_DIR, run_demo_file


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the SecureTheCloud brokered delegation local demo."
    )
    parser.add_argument(
        "request_file",
        type=Path,
        help="Path to a sample request JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_RUNS_DIR,
        help="Directory where evidence JSON should be written.",
    )
    parser.add_argument(
        "--now-epoch",
        type=int,
        default=None,
        help="Optional fixed epoch timestamp for deterministic demos/tests.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    evidence, output_path = run_demo_file(
        args.request_file,
        output_dir=args.output_dir,
        now_epoch=args.now_epoch,
    )

    summary = {
        "request_id": evidence.get("request_id"),
        "policy_decision": evidence.get("policy_decision"),
        "token_exchange": evidence.get("token_exchange"),
        "api_access": evidence.get("api_access"),
        "api_authorization_decision": evidence.get("api_authorization_decision"),
        "evidence_path": str(output_path),
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
