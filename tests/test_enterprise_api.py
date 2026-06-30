from brokered_delegation.enterprise_api import (
    call_knowledge_api,
    call_ticketing_api,
    validate_api_access,
)
from brokered_delegation.token_broker import exchange_token


def _ticket_token():
    result = exchange_token(
        {
            "request_id": "T201",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        },
        now_epoch=1000,
    )
    assert result.delegated_token is not None
    return result.delegated_token


def _runbook_token():
    result = exchange_token(
        {
            "request_id": "T202",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "knowledge-api",
            "action": "knowledge.read_runbook",
            "requested_scope": "runbook:read",
        },
        now_epoch=1000,
    )
    assert result.delegated_token is not None
    return result.delegated_token


def test_ticketing_api_accepts_valid_ticket_token():
    token = _ticket_token()

    result = call_ticketing_api(token, now_epoch=1200)

    evidence = result.to_evidence_update()
    assert evidence["api_access"] == "ALLOW"
    assert evidence["reason_code"] == "API_ACCESS_GRANTED"
    assert evidence["token_audience"] == "ticketing-api"
    assert evidence["token_scope"] == "ticket:create"
    assert evidence["token_subject"] == "alice@example.com"
    assert evidence["token_actor"] == "support-agent-001"
    assert evidence["raw_token_logged"] is False


def test_ticketing_api_rejects_wrong_audience_token():
    token = _runbook_token()

    result = call_ticketing_api(token, now_epoch=1200)

    assert result.api_access == "DENY"
    assert result.reason_code == "TOKEN_AUDIENCE_MISMATCH"
    assert result.token_audience == "knowledge-api"
    assert result.raw_token_logged is False


def test_knowledge_api_rejects_ticketing_audience_token():
    token = _ticket_token()

    result = call_knowledge_api(token, now_epoch=1200)

    assert result.api_access == "DENY"
    assert result.reason_code == "TOKEN_AUDIENCE_MISMATCH"
    assert result.token_audience == "ticketing-api"


def test_api_rejects_expired_token():
    token = _ticket_token()

    result = call_ticketing_api(token, now_epoch=1300)

    assert result.api_access == "DENY"
    assert result.reason_code == "TOKEN_EXPIRED"
    assert result.token_expired is True


def test_api_rejects_insufficient_scope():
    claims = _ticket_token().to_claims()
    claims["scope"] = "ticket:read"

    result = call_ticketing_api(claims, now_epoch=1200)

    assert result.api_access == "DENY"
    assert result.reason_code == "TOKEN_SCOPE_INSUFFICIENT"
    assert result.token_scope == "ticket:read"


def test_api_rejects_missing_delegation_context():
    claims = _ticket_token().to_claims()
    claims.pop("act")

    result = call_ticketing_api(claims, now_epoch=1200)

    assert result.api_access == "DENY"
    assert result.reason_code == "DELEGATION_CONTEXT_MISSING"


def test_api_rejects_missing_token():
    result = validate_api_access(
        None,
        target_app="ticketing-api",
        required_scope="ticket:create",
        now_epoch=1200,
    )

    assert result.api_access == "DENY"
    assert result.reason_code == "TOKEN_MISSING"


def test_api_rejects_unknown_target_app():
    result = validate_api_access(
        _ticket_token(),
        target_app="unknown-api",
        required_scope="ticket:create",
        now_epoch=1200,
    )

    assert result.api_access == "DENY"
    assert result.reason_code == "TARGET_APP_UNKNOWN"
