from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .config_loader import load_config
from .oidc_claims import OIDCValidationResult, validate_oidc_claims
from .policy_engine import Decision, evaluate_request


@dataclass(frozen=True)
class IdentityMappingResult:
    """Result of mapping validated external identity claims into local policy context."""

    mapped: bool
    reason_code: str
    user_id: str | None = None
    subject: str | None = None
    email: str | None = None
    groups: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    raw_token_logged: bool = False

    def to_evidence_update(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["identity_mapped"] = payload.pop("mapped")
        payload["identity_reason_code"] = payload.pop("reason_code")
        return {key: value for key, value in payload.items() if value not in (None, (), [])}


@dataclass(frozen=True)
class ExternalIdentityPolicyResult:
    """Combined external-identity validation, mapping, and policy result."""

    validation: OIDCValidationResult
    mapping: IdentityMappingResult
    decision: Decision | None = None

    @property
    def allowed(self) -> bool:
        return self.decision is not None and self.decision.policy_decision == "ALLOW"

    def to_evidence_update(self) -> dict[str, Any]:
        evidence = {}
        evidence.update(self.validation.to_evidence_update())
        evidence.update(self.mapping.to_evidence_update())
        if self.decision is not None:
            evidence.update({f"policy_{key}": value for key, value in self.decision.to_evidence().items()})
        return evidence


def _by_key(items: list[dict[str, Any]], key: str, value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return next((item for item in items if item.get(key) == value), None)


def _known_groups(config: dict[str, Any]) -> set[str]:
    groups: set[str] = set()
    for user in config.get("users", []):
        groups.update(str(group) for group in user.get("groups", []))
    return groups


def map_claims_to_user_context(
    claims: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> IdentityMappingResult:
    """Map validated OIDC-style claims to an existing local user profile.

    This intentionally maps into the current config-driven policy model instead
    of creating a second authorization system.
    """
    config = config or load_config()
    subject = claims.get("sub")
    email = claims.get("email")
    groups = tuple(str(group) for group in claims.get("groups", []) if str(group))
    scopes_value = claims.get("scp", claims.get("scope", []))
    if isinstance(scopes_value, str):
        scopes = tuple(item for item in scopes_value.split() if item)
    else:
        scopes = tuple(str(scope) for scope in scopes_value if str(scope))

    if not subject:
        return IdentityMappingResult(False, "SUBJECT_MISSING")

    known_groups = _known_groups(config)
    unknown_groups = [group for group in groups if group not in known_groups]
    if unknown_groups:
        return IdentityMappingResult(
            False,
            "UNKNOWN_GROUP",
            subject=str(subject),
            email=str(email) if email else None,
            groups=groups,
            scopes=scopes,
        )

    user = _by_key(config.get("users", []), "user_id", str(email) if email else None)
    if user is None:
        user = _by_key(config.get("users", []), "user_id", str(subject))

    if user is None:
        return IdentityMappingResult(
            False,
            "USER_MAPPING_NOT_FOUND",
            subject=str(subject),
            email=str(email) if email else None,
            groups=groups,
            scopes=scopes,
        )

    user_groups = set(user.get("groups", []))
    if groups and not user_groups.intersection(groups):
        return IdentityMappingResult(
            False,
            "GROUP_NOT_ASSIGNED_TO_USER",
            user_id=str(user.get("user_id")),
            subject=str(subject),
            email=str(email) if email else None,
            groups=groups,
            scopes=scopes,
        )

    return IdentityMappingResult(
        True,
        "USER_MAPPED_TO_LOCAL_POLICY_CONTEXT",
        user_id=str(user.get("user_id")),
        subject=str(subject),
        email=str(email) if email else None,
        groups=groups,
        scopes=scopes,
        raw_token_logged=False,
    )


def build_policy_request_from_claims(
    claims: dict[str, Any],
    request_template: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
) -> tuple[IdentityMappingResult, dict[str, Any] | None]:
    """Build an existing policy-engine request from external identity claims."""
    mapping = map_claims_to_user_context(claims, config=config)
    if not mapping.mapped or mapping.user_id is None:
        return mapping, None

    requested_scope = request_template.get("requested_scope")
    if requested_scope and requested_scope not in mapping.scopes:
        return (
            IdentityMappingResult(
                False,
                "CLAIMS_SCOPE_DOES_NOT_INCLUDE_REQUESTED_SCOPE",
                user_id=mapping.user_id,
                subject=mapping.subject,
                email=mapping.email,
                groups=mapping.groups,
                scopes=mapping.scopes,
            ),
            None,
        )

    request = dict(request_template)
    request["user"] = mapping.user_id
    return mapping, request


def evaluate_request_from_claims(
    claims: dict[str, Any],
    request_template: dict[str, Any],
    *,
    config: dict[str, Any] | None = None,
    now_epoch: int | None = None,
) -> ExternalIdentityPolicyResult:
    """Validate external claims, map identity, and call the existing policy engine."""
    validation = validate_oidc_claims(claims, now_epoch=now_epoch)
    if not validation.valid:
        return ExternalIdentityPolicyResult(
            validation=validation,
            mapping=IdentityMappingResult(False, "IDENTITY_VALIDATION_FAILED"),
            decision=None,
        )

    mapping, policy_request = build_policy_request_from_claims(
        claims,
        request_template,
        config=config,
    )
    if not mapping.mapped or policy_request is None:
        return ExternalIdentityPolicyResult(validation=validation, mapping=mapping, decision=None)

    decision = evaluate_request(policy_request, config=config)
    return ExternalIdentityPolicyResult(validation=validation, mapping=mapping, decision=decision)
