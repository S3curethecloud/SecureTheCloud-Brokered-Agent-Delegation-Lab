# Phase 5A: External JWT/OIDC Claim Validation Simulation

## Purpose

Phase 5A adds a deterministic, non-secret simulation for validating external OIDC-style claims and mapping them into the existing local policy model.

This phase still does not use a live Okta tenant. It uses sample claim JSON files so the repo can prove the identity-mapping contract before live IdP configuration.

## Goal

```text
sample OIDC claims
  -> validate issuer/audience/exp/sub
  -> map groups/scopes to local user policy context
  -> feed existing policy engine
  -> preserve fail-closed behavior
```

## Added Components

| File | Purpose |
|---|---|
| `src/brokered_delegation/oidc_claims.py` | Validates non-secret OIDC-style claims. |
| `src/brokered_delegation/identity_mapper.py` | Maps validated claims to local policy user context. |
| `samples/oidc/sample-access-token-claims.json` | Valid sample claims for Alice. |
| `samples/oidc/sample-invalid-token-claims.json` | Invalid sample claims for fail-closed validation. |
| `tests/test_oidc_claims.py` | Tests issuer, audience, expiration, subject, scope, and group validation. |
| `tests/test_identity_mapper.py` | Tests identity mapping and policy-engine integration. |

## Claim Validation Rules

The simulation validates:

| Claim | Rule |
|---|---|
| `iss` | Must match a trusted issuer. |
| `sub` | Must be present. |
| `aud` | Must match the expected audience. |
| `exp` | Must be present and not expired. |
| `iat` | Must be present and valid. |
| `scp` or `scope` | Must contain at least one scope. |
| `groups` | Must contain at least one group. |
| `email` | Used for local user mapping when present. |

## Identity Mapping Rules

The mapper follows these rules:

1. Validate external claims before policy evaluation.
2. Map `email` or `sub` to an existing local user.
3. Reject unknown groups.
4. Reject users that cannot be mapped to local policy context.
5. Reject requests when the requested scope is not present in the external claim set.
6. Feed only the normalized request into the existing policy engine.

## Sample Valid Claims

```json
{
  "iss": "https://idp.example.com/oauth2/default",
  "sub": "00u-alice-support-lead",
  "aud": "brokered-agent-delegation-lab",
  "exp": 4102444800,
  "iat": 1893456000,
  "email": "alice@example.com",
  "groups": ["customer-support"],
  "scp": ["customer:read", "ticket:create", "ticket:read", "runbook:read"]
}
```

## Fail-Closed Conditions

The simulation rejects claims when:

- issuer is missing or untrusted
- subject is missing
- audience does not match
- token is expired
- issued-at value is missing or invalid
- scopes are missing
- groups are missing
- group is unknown
- user cannot be mapped
- requested scope is not present in the external claims

## Policy Engine Integration

The identity mapper does not bypass local policy.

It builds the same request shape already used by the policy engine:

```json
{
  "request_id": "T501",
  "user": "alice@example.com",
  "agent": "support-agent-001",
  "target_app": "ticketing-api",
  "action": "ticketing.create_ticket",
  "requested_scope": "ticket:create"
}
```

Then it calls the existing deterministic policy engine.

## Why This Matters

This phase proves that external identity will be treated as an input to policy, not as automatic authorization.

A valid OIDC token does not automatically mean the agent can act. The request must still pass user permission, agent capability, target app, requested scope, data classification, and risk checks.

## Security Invariant

```text
Validated identity is not authorization.
Authorization remains policy-driven.
```

## Validation

Run:

```bash
make validate
```

Expected after Phase 5A:

```text
43 passed
```

## Next Phase

After Phase 5A, the next phase should introduce an external-token-validator interface that can later support real JWKS validation without changing the policy engine contract.
