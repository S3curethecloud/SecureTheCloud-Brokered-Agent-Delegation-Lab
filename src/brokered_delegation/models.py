from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class DelegatedToken:
    """Structured mock delegated token claims.

    This is intentionally not a bearer token string. The lab models token claims
    and security behavior without encouraging raw token logging.
    """

    issuer: str
    subject: str
    actor: str
    audience: str
    scope: str
    issued_at: int
    expires_at: int
    jwt_id: str
    delegation_type: str = "on_behalf_of"

    def to_claims(self) -> dict[str, Any]:
        return {
            "iss": self.issuer,
            "sub": self.subject,
            "act": {"sub": self.actor},
            "aud": self.audience,
            "scope": self.scope,
            "delegation_type": self.delegation_type,
            "iat": self.issued_at,
            "exp": self.expires_at,
            "jti": self.jwt_id,
        }

    def is_expired(self, at_epoch: int | None = None) -> bool:
        now = at_epoch if at_epoch is not None else int(datetime.now(UTC).timestamp())
        return now >= self.expires_at


@dataclass(frozen=True)
class TokenExchangeResult:
    """Result returned by the token broker after a policy decision."""

    request_id: str
    token_exchange: str
    reason_code: str
    policy_decision: str
    delegated_token: DelegatedToken | None = None
    raw_token_logged: bool = False

    def to_evidence_update(self) -> dict[str, Any]:
        payload = asdict(self)
        token = payload.pop("delegated_token", None)
        if token:
            payload["token_audience"] = token["audience"]
            payload["token_scope"] = token["scope"]
            payload["token_ttl_seconds"] = token["expires_at"] - token["issued_at"]
            payload["token_jti"] = token["jwt_id"]
        return {key: value for key, value in payload.items() if value is not None}
