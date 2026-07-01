# Build Roadmap

## Phase 0 — Repository Foundation

Status: Complete

Goal: Establish the Source of Truth and architecture contract.

Deliverables:

- README
- Source of Truth
- Architecture overview
- Threat model
- Token exchange model
- Agent capability model
- Policy decision model
- Evidence model
- Repo-native SVG infographic
- Config skeletons
- Policy skeletons
- Evidence examples

## Phase 1 — Deterministic Policy Simulation

Status: Complete

Goal: Build the first runnable authorization decision loop.

Deliverables:

- Local Python policy evaluator
- Config loader for users, apps, agents, and scopes
- Allow/deny decision output
- Evidence record generation
- Unit tests for primary abuse cases

## Phase 2 — Mock Token Broker

Status: Complete

Goal: Simulate OAuth-style delegated token issuance.

Deliverables:

- Token broker service
- Mock delegated token object
- `sub`, `act`, `aud`, `scope`, `iat`, `exp`, and `jti` claims
- Token exchange denied unless policy returns `ALLOW`
- Evidence record for token exchange

## Phase 3 — Mock Enterprise APIs

Status: Complete

Goal: Prove downstream systems independently enforce delegated token constraints.

Deliverables:

- Mock CRM API validator
- Mock Ticketing API validator
- Mock Knowledge API validator
- Audience validation
- Scope validation
- Expiration validation
- Delegation context validation
- API access evidence updates

## Phase 4A — Local Demo Runner and Evidence Output

Status: Complete

Goal: Make the lab demo-friendly by generating full-chain evidence from a sample request.

Deliverables:

- Local demo runner module
- CLI script for sample request execution
- Evidence output directory
- Demo evidence JSON generation
- Tests for successful and denied demo paths
- Documentation for operator usage

## Phase 4A.1 — Evidence Review CLI and Demo Summary

Status: Complete

Goal: Turn generated evidence into a clean, readable summary for interviews and live demos.

Deliverables:

- Evidence review utility module
- Latest-evidence CLI script
- Makefile shortcut for evidence review
- Demo walkthrough documentation
- Tests for evidence loading, latest-file selection, and summary formatting

## Phase 4B — Okta / OIDC Integration Planning Gate

Status: Complete

Goal: Map the local pattern to a real enterprise identity provider without introducing secrets or tenant-specific values.

Deliverables:

- Okta/OIDC integration planning document
- OAuth token exchange mapping document
- Production hardening checklist
- OIDC claim mapping plan
- External token exchange boundary plan
- No-secret integration gate

## Phase 5A — External JWT/OIDC Claim Validation Simulation

Status: Implemented

Goal: Validate non-secret OIDC-style claims and map them into the existing local policy model without live Okta configuration.

Deliverables:

- OIDC claim validation module
- Identity mapper module
- Non-secret valid sample claim payload
- Non-secret invalid sample claim payload
- Tests for issuer, audience, expiration, subject, scope, and group validation
- Tests for claim-to-policy mapping and fail-closed behavior
- Documentation for external claims validation

Core tests:

- Trusted issuer claims are accepted
- Untrusted issuer claims are rejected
- Wrong audience is rejected
- Expired claims are rejected
- Missing subject is rejected
- Missing scopes are rejected
- Valid claims map to an existing local user
- Unknown groups fail closed
- Unknown users fail closed
- Requested scope must exist in external claims
- Mapped request is evaluated by the existing policy engine

Security invariant:

```text
Validated identity is not authorization.
Authorization remains policy-driven.
```

## Phase 5B — External Token Validator Interface

Status: Next

Goal: Add an interface boundary that can later support JWKS-backed external token validation without changing the local policy engine contract.

Deliverables:

- External token validator interface
- Mock JWKS-ready validation boundary
- Tests for validator success/failure paths
- Evidence fields for issuer, audience, validation result, and raw-token exclusion
- No committed tenant secrets

## Recommended Build Order

1. Keep Phase 0 documentation locked before coding.
2. Implement the policy decision loop first.
3. Add token broker only after allow/deny behavior is tested.
4. Add mock APIs after token shape is stable.
5. Add local demo runner before external IdP integration.
6. Add evidence review before external IdP integration.
7. Add OIDC/token-exchange planning before live IdP configuration.
8. Add non-secret external claims simulation before live token validation.
9. Add external validator interfaces only after claim mapping is tested.

This prevents the lab from turning into an identity-provider configuration exercise before the agent security pattern is proven.
