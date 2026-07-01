"""SecureTheCloud Brokered Agent Delegation Lab."""

from .demo_runner import load_request, run_demo_file, run_demo_request
from .enterprise_api import (
    ApiAccessResult,
    call_crm_api,
    call_knowledge_api,
    call_ticketing_api,
    validate_api_access,
)
from .evidence_review import (
    latest_evidence_file,
    list_evidence_files,
    load_evidence,
    summarize_evidence,
    summarize_latest_evidence,
)
from .identity_mapper import (
    ExternalIdentityPolicyResult,
    IdentityMappingResult,
    build_policy_request_from_claims,
    evaluate_request_from_claims,
    map_claims_to_user_context,
)
from .models import DelegatedToken, TokenExchangeResult
from .oidc_claims import (
    DEFAULT_EXPECTED_AUDIENCE,
    DEFAULT_TRUSTED_ISSUERS,
    OIDCValidationResult,
    audience_matches,
    normalize_claim_values,
    validate_oidc_claims,
)
from .policy_engine import Decision, evaluate_request
from .token_broker import build_delegation_evidence, exchange_token, exchange_token_from_decision

__all__ = [
    "ApiAccessResult",
    "DEFAULT_EXPECTED_AUDIENCE",
    "DEFAULT_TRUSTED_ISSUERS",
    "Decision",
    "DelegatedToken",
    "ExternalIdentityPolicyResult",
    "IdentityMappingResult",
    "OIDCValidationResult",
    "TokenExchangeResult",
    "audience_matches",
    "build_delegation_evidence",
    "build_policy_request_from_claims",
    "call_crm_api",
    "call_knowledge_api",
    "call_ticketing_api",
    "evaluate_request",
    "evaluate_request_from_claims",
    "exchange_token",
    "exchange_token_from_decision",
    "latest_evidence_file",
    "list_evidence_files",
    "load_evidence",
    "load_request",
    "map_claims_to_user_context",
    "normalize_claim_values",
    "run_demo_file",
    "run_demo_request",
    "summarize_evidence",
    "summarize_latest_evidence",
    "validate_api_access",
    "validate_oidc_claims",
]
