#!/usr/bin/env python
from __future__ import annotations

import argparse
from pathlib import Path

from brokered_delegation.demo_runner import DEFAULT_EVIDENCE_RUNS_DIR
from brokered_delegation.evidence_review import summarize_latest_evidence


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Show the latest SecureTheCloud brokered delegation evidence summary."
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=DEFAULT_EVIDENCE_RUNS_DIR,
        help="Directory containing generated evidence JSON files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    path, summary = summarize_latest_evidence(args.evidence_dir)
    print(summary)
    print(f"Evidence File: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
