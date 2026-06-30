import json
import os
import time

import pytest

from brokered_delegation.evidence_review import (
    latest_evidence_file,
    list_evidence_files,
    load_evidence,
    summarize_evidence,
    summarize_latest_evidence,
)


def _write_evidence(path, request_id):
    evidence = {
        "request_id": request_id,
        "policy_decision": "ALLOW",
        "token_exchange": "SUCCESS",
        "api_authorization_decision": "ALLOW",
        "api_access": "SUCCESS",
        "user": "alice@example.com",
        "agent": "support-agent-001",
        "target_app": "ticketing-api",
        "requested_scope": "ticket:create",
        "token_audience": "ticketing-api",
        "api_reason_code": "API_ACCESS_GRANTED",
        "raw_token_logged": False,
    }
    path.write_text(json.dumps(evidence), encoding="utf-8")
    return evidence


def test_list_and_latest_evidence_file(tmp_path):
    older = tmp_path / "older.json"
    newer = tmp_path / "newer.json"
    _write_evidence(older, "older-request")
    time.sleep(0.01)
    _write_evidence(newer, "newer-request")

    files = list_evidence_files(tmp_path)

    assert files == [older, newer]
    assert latest_evidence_file(tmp_path) == newer


def test_latest_evidence_file_raises_when_empty(tmp_path):
    with pytest.raises(FileNotFoundError):
        latest_evidence_file(tmp_path)


def test_load_and_summarize_evidence(tmp_path):
    evidence_path = tmp_path / "evidence.json"
    evidence = _write_evidence(evidence_path, "sample-allow-ticket-create")

    loaded = load_evidence(evidence_path)
    summary = summarize_evidence(loaded)

    assert loaded == evidence
    assert "SecureTheCloud Brokered Delegation Evidence Summary" in summary
    assert "Request: sample-allow-ticket-create" in summary
    assert "Policy: ALLOW" in summary
    assert "Token Exchange: SUCCESS" in summary
    assert "API Decision: ALLOW" in summary
    assert "User: alice@example.com" in summary
    assert "Agent: support-agent-001" in summary
    assert "Target App: ticketing-api" in summary
    assert "Scope: ticket:create" in summary
    assert "Raw Token Logged: false" in summary


def test_summarize_latest_evidence(tmp_path):
    evidence_path = tmp_path / "latest.json"
    _write_evidence(evidence_path, "latest-request")
    os.utime(evidence_path, None)

    path, summary = summarize_latest_evidence(tmp_path)

    assert path == evidence_path
    assert "Request: latest-request" in summary
    assert "API Reason: API_ACCESS_GRANTED" in summary
