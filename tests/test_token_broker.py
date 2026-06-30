from brokered_delegation.token_broker import build_delegation_evidence, exchange_token


def test_policy_allow_issues_delegated_token():
    result = exchange_token(
        {
            "request_id": "T101",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        },
        now_epoch=1_893_456_700,
    )

    assert result.token_exchange == "SUCCESS"
    assert result.delegated_token is not None

    claims = result.delegated_token.to_claims()
    assert claims["iss"] == "securethecloud-token-broker"
    assert claims["sub"] == "alice@example.com"
    assert claims["act"]["sub"] == "support-agent-001"
    assert claims["aud"] == "ticketing-api"
    assert claims["scope"] == "ticket:create"
    assert claims["delegation_type"] == "on_behalf_of"
    assert claims["iat"] == 1_893_456_700
    assert claims["exp"] == 1_893_457_000
    assert claims["jti"]
    assert result.raw_token_logged is False


def test_policy_deny_does_not_issue_token():
    result = exchange_token(
        {
            "request_id": "T102",
            "user": "bob@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        },
        now_epoch=1_893_456_700,
    )

    assert result.token_exchange == "NOT_ATTEMPTED"
    assert result.delegated_token is None
    assert result.policy_decision == "DENY"
    assert result.reason_code == "USER_LACKS_SCOPE"
    assert result.raw_token_logged is False


def test_token_ttl_respects_agent_max_ttl():
    result = exchange_token(
        {
            "request_id": "T103",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "knowledge-api",
            "action": "knowledge.read_runbook",
            "requested_scope": "runbook:read",
        },
        now_epoch=1_893_456_700,
    )

    claims = result.delegated_token.to_claims()
    assert claims["exp"] - claims["iat"] == 300


def test_delegated_token_expiration_check():
    result = exchange_token(
        {
            "request_id": "T104",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        },
        now_epoch=1000,
    )

    token = result.delegated_token
    assert token.is_expired(at_epoch=1299) is False
    assert token.is_expired(at_epoch=1300) is True


def test_evidence_contains_token_metadata_not_raw_token():
    evidence = build_delegation_evidence(
        {
            "request_id": "T105",
            "user": "alice@example.com",
            "agent": "support-agent-001",
            "target_app": "ticketing-api",
            "action": "ticketing.create_ticket",
            "requested_scope": "ticket:create",
        },
        now_epoch=1_893_456_700,
    )

    assert evidence["policy_decision"] == "ALLOW"
    assert evidence["token_exchange"] == "SUCCESS"
    assert evidence["token_audience"] == "ticketing-api"
    assert evidence["token_scope"] == "ticket:create"
    assert evidence["token_ttl_seconds"] == 300
    assert evidence["token_jti"]
    assert evidence["raw_token_logged"] is False
    assert "access_token" not in evidence
    assert "bearer" not in {key.lower() for key in evidence}
