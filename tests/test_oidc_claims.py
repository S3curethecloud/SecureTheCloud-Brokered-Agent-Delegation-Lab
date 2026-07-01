from brokered_delegation.oidc_claims import (
    audience_matches,
    normalize_claim_values,
    validate_oidc_claims,
)


VALID_CLAIMS = {
    "iss": "https://idp.example.com/oauth2/default",
    "sub": "00u-alice-support-lead",
    "aud": "brokered-agent-delegation-lab",
    "exp": 4102444800,
    "iat": 1893456000,
    "email": "alice@example.com",
    "groups": ["customer-support"],
    "scp": ["customer:read", "ticket:create", "runbook:read"],
}


def test_normalize_claim_values_handles_string_and_list():
    assert normalize_claim_values("ticket:create runbook:read") == ("ticket:create", "runbook:read")
    assert normalize_claim_values(["customer:read", "ticket:read"]) == ("customer:read", "ticket:read")
    assert normalize_claim_values(None) == ()


def test_audience_matches_string_and_list():
    assert audience_matches("brokered-agent-delegation-lab", "brokered-agent-delegation-lab") is True
    assert audience_matches(["other-api", "brokered-agent-delegation-lab"], "brokered-agent-delegation-lab") is True
    assert audience_matches("other-api", "brokered-agent-delegation-lab") is False


def test_valid_oidc_claims_are_accepted():
    result = validate_oidc_claims(VALID_CLAIMS, now_epoch=2000)

    assert result.valid is True
    assert result.reason_code == "OIDC_CLAIMS_VALIDATED"
    assert result.issuer == "https://idp.example.com/oauth2/default"
    assert result.subject == "00u-alice-support-lead"
    assert result.audience == "brokered-agent-delegation-lab"
    assert result.email == "alice@example.com"
    assert "ticket:create" in result.scopes
    assert "customer-support" in result.groups
    assert result.raw_token_logged is False


def test_untrusted_issuer_is_rejected():
    claims = dict(VALID_CLAIMS)
    claims["iss"] = "https://untrusted-idp.example.com/oauth2/default"

    result = validate_oidc_claims(claims, now_epoch=2000)

    assert result.valid is False
    assert result.reason_code == "ISSUER_UNTRUSTED"


def test_audience_mismatch_is_rejected():
    claims = dict(VALID_CLAIMS)
    claims["aud"] = "wrong-audience"

    result = validate_oidc_claims(claims, now_epoch=2000)

    assert result.valid is False
    assert result.reason_code == "AUDIENCE_MISMATCH"


def test_expired_claims_are_rejected():
    claims = dict(VALID_CLAIMS)
    claims["exp"] = 1000

    result = validate_oidc_claims(claims, now_epoch=2000)

    assert result.valid is False
    assert result.reason_code == "TOKEN_EXPIRED"


def test_missing_subject_is_rejected():
    claims = dict(VALID_CLAIMS)
    claims.pop("sub")

    result = validate_oidc_claims(claims, now_epoch=2000)

    assert result.valid is False
    assert result.reason_code == "SUBJECT_MISSING"


def test_missing_scope_is_rejected():
    claims = dict(VALID_CLAIMS)
    claims.pop("scp")

    result = validate_oidc_claims(claims, now_epoch=2000)

    assert result.valid is False
    assert result.reason_code == "SCOPES_MISSING"
