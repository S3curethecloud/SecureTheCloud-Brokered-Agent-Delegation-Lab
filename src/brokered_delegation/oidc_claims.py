from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

DEFAULT_TRUSTED_ISSUERS = {"https://idp.example.com/oauth2/default"}
DEFAULT_EXPECTED_AUDIENCE = "brokered-agent-delegation-lab"


@dataclass(frozen=True)
class OIDCValidationResult:
    """Deterministic validation result for external OIDC-style claims."""

    valid: bool
    reason_code: str
    issuer: str | None = None
    subject: str | None = None
    audience: str | None = None
    expires_at: int | None = None
    issued_at: int | None = None
    scopes: tuple[str, ...] = ()
    groups: tuple[str, ...] = ()
    email: str | None = None
    raw_token_logged: bool = False

    def to_evidence_update(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["oidc_valid"] = payload.pop("valid")
        payload["oidc_reason_code"] = payload.pop("reason_code")
        return {key: value for key, value in payload.items() if value not in (None, (), [])}


def _now_epoch() -> int:
    return int(datetime.now(UTC).timestamp())


def normalize_claim_values(value: Any) -> tuple[str, ...]:
    """Normalize a string/list claim into a tuple of strings."""
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(item for item in value.split() if item)
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item))
    return (str(value),)


def audience_matches(audience_claim: Any, expected_audience: str) -> bool:
    """Handle OIDC/OAuth audience values represented as string or list."""
    if isinstance(audience_claim, str):
        return audience_claim == expected_audience
    if isinstance(audience_claim, list):
        return expected_audience in {str(item) for item in audience_claim}
    return False


def validate_oidc_claims(
    claims: dict[str, Any],
    *,
    trusted_issuers: set[str] | None = None,
    expected_audience: str = DEFAULT_EXPECTED_AUDIENCE,
    now_epoch: int | None = None,
) -> OIDCValidationResult:
    """Validate non-secret OIDC-style claims before policy evaluation.

    This is a deterministic simulation. It validates claim shape and trust
    decisions, but it does not validate a JWT signature because no live IdP or
    JWKS endpoint is used in Phase 5A.
    """
    trusted_issuers = trusted_issuers or DEFAULT_TRUSTED_ISSUERS
    now = now_epoch if now_epoch is not None else _now_epoch()

    if not isinstance(claims, dict):
        return OIDCValidationResult(False, "CLAIMS_NOT_OBJECT")

    issuer = claims.get("iss")
    subject = claims.get("sub")
    audience = claims.get("aud")
    expires_at = claims.get("exp")
    issued_at = claims.get("iat")
    scopes = normalize_claim_values(claims.get("scp", claims.get("scope")))
    groups = normalize_claim_values(claims.get("groups"))
    email = claims.get("email")

    if not issuer:
        return OIDCValidationResult(False, "ISSUER_MISSING")
    if issuer not in trusted_issuers:
        return OIDCValidationResult(False, "ISSUER_UNTRUSTED", issuer=str(issuer))
    if not subject:
        return OIDCValidationResult(False, "SUBJECT_MISSING", issuer=str(issuer))
    if not audience_matches(audience, expected_audience):
        return OIDCValidationResult(
            False,
            "AUDIENCE_MISMATCH",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            scopes=scopes,
            groups=groups,
            email=str(email) if email else None,
        )
    if not isinstance(expires_at, int):
        return OIDCValidationResult(
            False,
            "EXPIRATION_MISSING_OR_INVALID",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            scopes=scopes,
            groups=groups,
            email=str(email) if email else None,
        )
    if now >= expires_at:
        return OIDCValidationResult(
            False,
            "TOKEN_EXPIRED",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            expires_at=expires_at,
            issued_at=issued_at if isinstance(issued_at, int) else None,
            scopes=scopes,
            groups=groups,
            email=str(email) if email else None,
        )
    if not isinstance(issued_at, int):
        return OIDCValidationResult(
            False,
            "ISSUED_AT_MISSING_OR_INVALID",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            expires_at=expires_at,
            scopes=scopes,
            groups=groups,
            email=str(email) if email else None,
        )
    if not scopes:
        return OIDCValidationResult(
            False,
            "SCOPES_MISSING",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            expires_at=expires_at,
            issued_at=issued_at,
            groups=groups,
            email=str(email) if email else None,
        )
    if not groups:
        return OIDCValidationResult(
            False,
            "GROUPS_MISSING",
            issuer=str(issuer),
            subject=str(subject),
            audience=str(audience),
            expires_at=expires_at,
            issued_at=issued_at,
            scopes=scopes,
            email=str(email) if email else None,
        )

    return OIDCValidationResult(
        True,
        "OIDC_CLAIMS_VALIDATED",
        issuer=str(issuer),
        subject=str(subject),
        audience=expected_audience,
        expires_at=expires_at,
        issued_at=issued_at,
        scopes=scopes,
        groups=groups,
        email=str(email) if email else None,
        raw_token_logged=False,
    )
