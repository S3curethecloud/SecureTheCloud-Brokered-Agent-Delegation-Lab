from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from .config_loader import load_config
from .models import DelegatedToken


@dataclass(frozen=True)
class ApiAccessResult:
    """Result of a downstream enterprise API authorization check."""

    api_access: str
    reason_code: str
    target_app: str
    required_scope: str
    token_audience: str | None = None
    token_scope: str | None = None
    token_subject: str | None = None
    token_actor: str | None = None
    token_expired: bool | None = None
    raw_token_logged: bool = False

    def to_evidence_update(self) -> dict[str, Any]:
        payload = asdict(self)
        return {key: value for key, value in payload.items() if value is not None}


def _now_epoch() -> int:
    return int(datetime.now(UTC).timestamp())


def _claims_from_token(token: DelegatedToken | dict[str, Any] | None) -> dict[str, Any] | None:
    if token is None:
        return None
    if isinstance(token, DelegatedToken):
        return token.to_claims()
    return token


def _scope_values(scope_value: Any) -> set[str]:
    if scope_value is None:
        return set()
    if isinstance(scope_value, str):
        return set(scope_value.split())
    if isinstance(scope_value, list):
        return {str(item) for item in scope_value}
    return {str(scope_value)}


def _known_app(target_app: str, config: dict[str, Any] | None = None) -> dict[str, Any] | None:
    config = config or load_config()
    return next((app for app in config["apps"] if app.get("app_id") == target_app), None)


def validate_api_access(
    token: DelegatedToken | dict[str, Any] | None,
    *,
    target_app: str,
    required_scope: str,
    now_epoch: int | None = None,
    config: dict[str, Any] | None = None,
) -> ApiAccessResult:
    """Validate delegated token claims at a mock enterprise API boundary.

    This models a critical enterprise security rule: downstream APIs must not
    blindly trust the agent gateway or token broker. Each API independently
    checks audience, scope, and token lifetime.
    """
    app = _known_app(target_app, config)
    if app is None:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TARGET_APP_UNKNOWN",
            target_app=target_app,
            required_scope=required_scope,
            raw_token_logged=False,
        )

    if required_scope not in app.get("accepted_scopes", []):
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TARGET_APP_DOES_NOT_ACCEPT_SCOPE",
            target_app=target_app,
            required_scope=required_scope,
            raw_token_logged=False,
        )

    claims = _claims_from_token(token)
    if not claims:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TOKEN_MISSING",
            target_app=target_app,
            required_scope=required_scope,
            raw_token_logged=False,
        )

    token_audience = claims.get("aud")
    token_scopes = _scope_values(claims.get("scope"))
    token_subject = claims.get("sub")
    token_actor = (claims.get("act") or {}).get("sub") if isinstance(claims.get("act"), dict) else None
    expires_at = claims.get("exp")
    now = now_epoch if now_epoch is not None else _now_epoch()
    token_expired = not isinstance(expires_at, int) or now >= expires_at

    if token_audience != target_app:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TOKEN_AUDIENCE_MISMATCH",
            target_app=target_app,
            required_scope=required_scope,
            token_audience=str(token_audience),
            token_scope=claims.get("scope"),
            token_subject=token_subject,
            token_actor=token_actor,
            token_expired=token_expired,
            raw_token_logged=False,
        )

    if token_expired:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TOKEN_EXPIRED",
            target_app=target_app,
            required_scope=required_scope,
            token_audience=str(token_audience),
            token_scope=claims.get("scope"),
            token_subject=token_subject,
            token_actor=token_actor,
            token_expired=True,
            raw_token_logged=False,
        )

    if required_scope not in token_scopes:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="TOKEN_SCOPE_INSUFFICIENT",
            target_app=target_app,
            required_scope=required_scope,
            token_audience=str(token_audience),
            token_scope=claims.get("scope"),
            token_subject=token_subject,
            token_actor=token_actor,
            token_expired=False,
            raw_token_logged=False,
        )

    if not token_subject or not token_actor:
        return ApiAccessResult(
            api_access="DENY",
            reason_code="DELEGATION_CONTEXT_MISSING",
            target_app=target_app,
            required_scope=required_scope,
            token_audience=str(token_audience),
            token_scope=claims.get("scope"),
            token_subject=token_subject,
            token_actor=token_actor,
            token_expired=False,
            raw_token_logged=False,
        )

    return ApiAccessResult(
        api_access="ALLOW",
        reason_code="API_ACCESS_GRANTED",
        target_app=target_app,
        required_scope=required_scope,
        token_audience=str(token_audience),
        token_scope=claims.get("scope"),
        token_subject=token_subject,
        token_actor=token_actor,
        token_expired=False,
        raw_token_logged=False,
    )


def call_crm_api(token: DelegatedToken | dict[str, Any] | None, *, now_epoch: int | None = None) -> ApiAccessResult:
    return validate_api_access(
        token,
        target_app="crm-api",
        required_scope="customer:read",
        now_epoch=now_epoch,
    )


def call_ticketing_api(token: DelegatedToken | dict[str, Any] | None, *, now_epoch: int | None = None) -> ApiAccessResult:
    return validate_api_access(
        token,
        target_app="ticketing-api",
        required_scope="ticket:create",
        now_epoch=now_epoch,
    )


def call_knowledge_api(token: DelegatedToken | dict[str, Any] | None, *, now_epoch: int | None = None) -> ApiAccessResult:
    return validate_api_access(
        token,
        target_app="knowledge-api",
        required_scope="runbook:read",
        now_epoch=now_epoch,
    )
