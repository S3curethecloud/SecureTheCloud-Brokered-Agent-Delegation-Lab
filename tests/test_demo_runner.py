import json
from pathlib import Path

from brokered_delegation.demo_runner import load_request, run_demo_file, run_demo_request


def test_demo_runner_writes_success_evidence(tmp_path):
    request = {
        "request_id": "T401",
        "user": "alice@example.com",
        "agent": "support-agent-001",
        "target_app": "ticketing-api",
        "action": "ticketing.create_ticket",
        "requested_scope": "ticket:create",
    }

    evidence, output_path = run_demo_request(request, output_dir=tmp_path, now_epoch=1000)

    assert output_path is not None
    assert output_path.exists()
    assert evidence["policy_decision"] == "ALLOW"
    assert evidence["token_exchange"] == "SUCCESS"
    assert evidence["api_access"] == "SUCCESS"
    assert evidence["api_authorization_decision"] == "ALLOW"
    assert evidence["api_reason_code"] == "API_ACCESS_GRANTED"
    assert evidence["token_audience"] == "ticketing-api"
    assert evidence["token_scope"] == "ticket:create"
    assert evidence["raw_token_logged"] is False
    assert "token_jti" in evidence

    written = json.loads(output_path.read_text(encoding="utf-8"))
    assert written["request_id"] == "T401"
    assert written["api_access"] == "SUCCESS"
    assert written["raw_token_logged"] is False
    assert "access_token" not in written
    assert "bearer" not in {key.lower() for key in written}


def test_demo_runner_records_denied_policy_without_token_or_api_call(tmp_path):
    request = {
        "request_id": "T402",
        "user": "bob@example.com",
        "agent": "support-agent-001",
        "target_app": "ticketing-api",
        "action": "ticketing.create_ticket",
        "requested_scope": "ticket:create",
    }

    evidence, output_path = run_demo_request(request, output_dir=tmp_path, now_epoch=1000)

    assert output_path is not None
    assert output_path.exists()
    assert evidence["policy_decision"] == "DENY"
    assert evidence["reason_code"] == "USER_LACKS_SCOPE"
    assert evidence["token_exchange"] == "NOT_ATTEMPTED"
    assert evidence["api_access"] == "NOT_ATTEMPTED"
    assert evidence["api_authorization_decision"] == "NOT_ATTEMPTED"
    assert evidence["api_reason_code"] == "TOKEN_NOT_ISSUED"
    assert evidence["raw_token_logged"] is False
    assert "token_jti" not in evidence


def test_load_request_and_run_demo_file(tmp_path):
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps(
            {
                "request_id": "T403",
                "user": "alice@example.com",
                "agent": "support-agent-001",
                "target_app": "knowledge-api",
                "action": "knowledge.read_runbook",
                "requested_scope": "runbook:read",
            }
        ),
        encoding="utf-8",
    )

    request = load_request(request_path)
    assert request["request_id"] == "T403"

    evidence, output_path = run_demo_file(request_path, output_dir=tmp_path, now_epoch=1000)
    assert output_path.exists()
    assert evidence["policy_decision"] == "ALLOW"
    assert evidence["token_exchange"] == "SUCCESS"
    assert evidence["api_authorization_decision"] == "ALLOW"
    assert evidence["api_target_app"] == "knowledge-api"
    assert evidence["api_required_scope"] == "runbook:read"
