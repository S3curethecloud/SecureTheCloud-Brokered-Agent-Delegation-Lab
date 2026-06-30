from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any

from .config_loader import load_config

RISK_ORDER = {"low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(frozen=True)
class Decision:
    request_id: str
    user: str
    agent: str
    target_app: str
    action: str
    requested_scope: str
    data_classification: str | None
    risk_tier: str | None
    policy_decision: str
    reason_code: str
    token_exchange: str
    api_access: str
    raw_token_logged: bool = False
    timestamp: str | None = None
    token_audience: str | None = None
    token_scope: str | None = None
    token_ttl_seconds: int | None = None

    def to_evidence(self) -> dict[str, Any]:
        evidence = asdict(self)
        evidence["timestamp"] = self.timestamp or datetime.now(UTC).isoformat()
        return {key: value for key, value in evidence.items() if value is not None}


def _by_key(items: list[dict[str, Any]], key: str, value: str) -> dict[str, Any] | None:
    return next((item for item in items if item.get(key) == value), None)


def _risk_allowed(requested: str | None, maximum: str | None) -> bool:
    if requested is None or maximum is None:
        return False
    return RISK_ORDER.get(requested, 999) <= RISK_ORDER.get(maximum, -1)


def evaluate_request(request: dict[str, Any], config: dict[str, Any] | None = None) -> Decision:
    """Evaluate a brokered delegation request.

    The policy is intentionally deterministic for Phase 1. It models the security
    contract before introducing live IdP or token broker integrations.
    """
    config = config or load_config()

    request_id = request.get("request_id", "req-unknown")
    user_id = request.get("user")
    agent_id = request.get("agent")
    target_app_id = request.get("target_app")
    action = request.get("action")
    requested_scope = request.get("requested_scope")

    user = _by_key(config["users"], "user_id", user_id)
    agent = _by_key(config["agents"], "agent_id", agent_id)
    app = _by_key(config["apps"], "app_id", target_app_id)
    scope = _by_key(config["scopes"], "scope", requested_scope)

    base = {
        "request_id": request_id,
        "user": user_id or "UNKNOWN_USER",
        "agent": agent_id or "UNKNOWN_AGENT",
        "target_app": target_app_id or "UNKNOWN_APP",
        "action": action or "UNKNOWN_ACTION",
        "requested_scope": requested_scope or "UNKNOWN_SCOPE",
        "data_classification": scope.get("data_classification") if scope else None,
        "risk_tier": scope.get("risk_tier") if scope else None,
        "raw_token_logged": False,
    }

    deny_reason = None
    if user is None:
        deny_reason = "USER_UNKNOWN"
    elif agent is None or agent.get("enabled", True) is False:
        deny_reason = "AGENT_UNKNOWN_OR_DISABLED"
    elif app is None:
        deny_reason = "TARGET_APP_UNKNOWN"
    elif scope is None:
        deny_reason = "SCOPE_UNKNOWN"
    elif requested_scope not in user.get("allowed_scopes", []):
        deny_reason = "USER_LACKS_SCOPE"
    elif action not in agent.get("allowed_tools", []):
        deny_reason = "AGENT_LACKS_CAPABILITY"
    elif target_app_id not in agent.get("allowed_target_apps", []):
        deny_reason = "AGENT_NOT_ALLOWED_FOR_TARGET_APP"
    elif requested_scope not in app.get("accepted_scopes", []):
        deny_reason = "TARGET_APP_DOES_NOT_ACCEPT_SCOPE"
    elif action not in app.get("allowed_actions", []):
        deny_reason = "TARGET_APP_DOES_NOT_ACCEPT_ACTION"
    elif scope.get("target_app") != target_app_id:
        deny_reason = "SCOPE_TARGET_APP_MISMATCH"
    elif scope.get("action") != action:
        deny_reason = "SCOPE_ACTION_MISMATCH"
    elif scope.get("data_classification") not in user.get("clearance", []):
        deny_reason = "USER_CLEARANCE_TOO_LOW"
    elif scope.get("data_classification") not in agent.get("allowed_data_classifications", []):
        deny_reason = "AGENT_CLASSIFICATION_NOT_ALLOWED"
    elif not _risk_allowed(scope.get("risk_tier"), user.get("max_risk_tier")):
        deny_reason = "USER_RISK_TIER_EXCEEDED"
    elif not _risk_allowed(scope.get("risk_tier"), agent.get("max_risk_tier")):
        deny_reason = "AGENT_RISK_TIER_EXCEEDED"

    if deny_reason:
        return Decision(
            **base,
            policy_decision="DENY",
            reason_code=deny_reason,
            token_exchange="NOT_ATTEMPTED",
            api_access="NOT_ATTEMPTED",
        )

    return Decision(
        **base,
        policy_decision="ALLOW",
        reason_code="USER_AND_AGENT_AUTHORIZED",
        token_exchange="SUCCESS",
        token_audience=target_app_id,
        token_scope=requested_scope,
        token_ttl_seconds=int(agent.get("token_ttl_seconds", 300)),
        api_access="SUCCESS",
    )
