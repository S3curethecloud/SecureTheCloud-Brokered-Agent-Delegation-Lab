from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from .models import DelegatedToken, TokenExchangeResult
from .policy_engine import Decision, evaluate_request

DEFAULT_ISSUER = "securethecloud-token-broker"


def exchange_token(
    request: dict,
    *,
    issuer: str = DEFAULT_ISSUER,
    now_epoch: int | None = None,
) -> TokenExchangeResult:
    """Evaluate policy and issue a mock delegated token when allowed.

    This function simulates the security behavior of an OAuth-style token broker.
    It never issues a delegated token when policy denies the request.
    """
    decision = evaluate_request(request)
    return exchange_token_from_decision(decision, issuer=issuer, now_epoch=now_epoch)


def exchange_token_from_decision(
    decision: Decision,
    *,
    issuer: str = DEFAULT_ISSUER,
    now_epoch: int | None = None,
) -> TokenExchangeResult:
    """Issue a delegated token only for an allowed policy decision."""
    if decision.policy_decision != "ALLOW":
        return TokenExchangeResult(
            request_id=decision.request_id,
            token_exchange="NOT_ATTEMPTED",
            reason_code=decision.reason_code,
            policy_decision=decision.policy_decision,
            delegated_token=None,
            raw_token_logged=False,
        )

    issued_at = now_epoch if now_epoch is not None else int(datetime.now(UTC).timestamp())
    ttl = int(decision.token_ttl_seconds or 300)
    expires_at = issued_at + ttl

    delegated_token = DelegatedToken(
        issuer=issuer,
        subject=decision.user,
        actor=decision.agent,
        audience=decision.target_app,
        scope=decision.requested_scope,
        issued_at=issued_at,
        expires_at=expires_at,
        jwt_id=str(uuid4()),
    )

    return TokenExchangeResult(
        request_id=decision.request_id,
        token_exchange="SUCCESS",
        reason_code="DELEGATED_TOKEN_ISSUED",
        policy_decision=decision.policy_decision,
        delegated_token=delegated_token,
        raw_token_logged=False,
    )


def build_delegation_evidence(request: dict, *, now_epoch: int | None = None) -> dict:
    """Return a combined policy + token-broker evidence record.

    The evidence record stores token metadata, not a raw bearer token.
    """
    decision = evaluate_request(request)
    evidence = decision.to_evidence()
    token_result = exchange_token_from_decision(decision, now_epoch=now_epoch)
    evidence.update(token_result.to_evidence_update())
    evidence["raw_token_logged"] = False
    return evidence
