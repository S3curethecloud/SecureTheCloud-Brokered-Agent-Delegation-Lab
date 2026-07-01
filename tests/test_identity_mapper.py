from brokered_delegation.identity_mapper import (
    build_policy_request_from_claims,
    evaluate_request_from_claims,
    map_claims_to_user_context,
)


VALID_CLAIMS = {
    "iss": "https://idp.example.com/oauth2/default",
    "sub": "00u-alice-support-lead",
    "aud": "brokered-agent-delegation-lab",
    "exp": 4102444800,
    "iat": 1893456000,
    "email": "alice@example.com",
    "groups": ["customer-support"],
    "scp": ["customer:read", "ticket:create", "ticket:read", "runbook:read"],
}


TICKET_REQUEST_TEMPLATE = {
    "request_id": "T501",
    "agent": "support-agent-001",
    "target_app": "ticketing-api",
    "action": "ticketing.create_ticket",
    "requested_scope": "ticket:create",
}


def test_maps_valid_claims_to_existing_local_user():
    result = map_claims_to_user_context(VALID_CLAIMS)

    assert result.mapped is True
    assert result.reason_code == "USER_MAPPED_TO_LOCAL_POLICY_CONTEXT"
    assert result.user_id == "alice@example.com"
    assert result.subject == "00u-alice-support-lead"
    assert result.email == "alice@example.com"
    assert "customer-support" in result.groups
    assert "ticket:create" in result.scopes
    assert result.raw_token_logged is False


def test_unknown_group_fails_closed():
    claims = dict(VALID_CLAIMS)
    claims["groups"] = ["unknown-group"]

    result = map_claims_to_user_context(claims)

    assert result.mapped is False
    assert result.reason_code == "UNKNOWN_GROUP"


def test_unknown_user_fails_closed():
    claims = dict(VALID_CLAIMS)
    claims["email"] = "unknown@example.com"

    result = map_claims_to_user_context(claims)

    assert result.mapped is False
    assert result.reason_code == "USER_MAPPING_NOT_FOUND"


def test_build_policy_request_from_claims_injects_mapped_user():
    mapping, policy_request = build_policy_request_from_claims(VALID_CLAIMS, TICKET_REQUEST_TEMPLATE)

    assert mapping.mapped is True
    assert policy_request is not None
    assert policy_request["user"] == "alice@example.com"
    assert policy_request["requested_scope"] == "ticket:create"
    assert policy_request["agent"] == "support-agent-001"


def test_build_policy_request_rejects_scope_not_present_in_claims():
    claims = dict(VALID_CLAIMS)
    claims["scp"] = ["customer:read"]

    mapping, policy_request = build_policy_request_from_claims(claims, TICKET_REQUEST_TEMPLATE)

    assert mapping.mapped is False
    assert mapping.reason_code == "CLAIMS_SCOPE_DOES_NOT_INCLUDE_REQUESTED_SCOPE"
    assert policy_request is None


def test_evaluate_request_from_claims_allows_valid_ticket_request():
    result = evaluate_request_from_claims(VALID_CLAIMS, TICKET_REQUEST_TEMPLATE, now_epoch=2000)

    assert result.validation.valid is True
    assert result.mapping.mapped is True
    assert result.decision is not None
    assert result.decision.policy_decision == "ALLOW"
    assert result.decision.reason_code == "USER_AND_AGENT_AUTHORIZED"
    assert result.decision.user == "alice@example.com"


def test_evaluate_request_from_claims_denies_when_claim_validation_fails():
    claims = dict(VALID_CLAIMS)
    claims["iss"] = "https://untrusted-idp.example.com/oauth2/default"

    result = evaluate_request_from_claims(claims, TICKET_REQUEST_TEMPLATE, now_epoch=2000)

    assert result.validation.valid is False
    assert result.validation.reason_code == "ISSUER_UNTRUSTED"
    assert result.mapping.mapped is False
    assert result.mapping.reason_code == "IDENTITY_VALIDATION_FAILED"
    assert result.decision is None


def test_evaluate_request_from_claims_denies_when_policy_denies():
    request_template = dict(TICKET_REQUEST_TEMPLATE)
    request_template["requested_scope"] = "customer:read"
    request_template["target_app"] = "crm-api"
    request_template["action"] = "ticketing.create_ticket"

    result = evaluate_request_from_claims(VALID_CLAIMS, request_template, now_epoch=2000)

    assert result.validation.valid is True
    assert result.mapping.mapped is True
    assert result.decision is not None
    assert result.decision.policy_decision == "DENY"
