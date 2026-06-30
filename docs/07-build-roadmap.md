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

Exit criteria:

- Repo can be cloned.
- Lab purpose is clear.
- Security invariants are documented.
- Future implementation phases have a stable contract.

## Phase 1 — Deterministic Policy Simulation

Status: Complete

Goal: Build the first runnable authorization decision loop.

Deliverables:

- Local Python policy evaluator
- Config loader for users, apps, agents, and scopes
- Allow/deny decision output
- Evidence record generation
- Unit tests for primary abuse cases

Core tests:

- `ALLOW` ticket creation for approved user and agent
- `DENY` restricted access from prompt-injection-style requests
- `DENY` broader scope than user has
- `DENY` unknown app
- `DENY` unknown agent

## Phase 2 — Mock Token Broker

Status: Complete

Goal: Simulate OAuth-style delegated token issuance.

Deliverables:

- Token broker service
- Mock delegated token object
- `sub`, `act`, `aud`, `scope`, `iat`, `exp`, and `jti` claims
- Token exchange denied unless policy returns `ALLOW`
- Evidence record for token exchange

Core tests:

- Token issued only after policy allow
- Token not issued after policy deny
- Token contains correct human subject and agent actor
- Token audience matches requested target app
- Token lifetime does not exceed allowed TTL
- Evidence stores metadata, not raw token material

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

Core tests:

- Ticketing accepts `ticket:create` token with `aud=ticketing-api`
- Ticketing rejects Knowledge API audience token
- Knowledge API rejects Ticketing audience token
- API rejects expired token
- API rejects insufficient scope
- API rejects missing delegation context
- API rejects missing token
- API rejects unknown target app

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

Core tests:

- Successful request writes evidence JSON
- Denied request does not issue a delegated token
- Denied request does not call downstream API
- Request file can be loaded and executed
- Evidence contains metadata, not raw token material

## Phase 4A.1 — Evidence Review CLI and Demo Summary

Status: Complete

Goal: Turn generated evidence into a clean, readable summary for interviews and live demos.

Deliverables:

- Evidence review utility module
- Latest-evidence CLI script
- Makefile shortcut for evidence review
- Demo walkthrough documentation
- Tests for evidence loading, latest-file selection, and summary formatting

Core tests:

- Latest evidence file can be discovered
- Empty evidence directory fails clearly
- Evidence JSON can be loaded
- Human-readable summary includes request, policy, token, API, user, agent, app, scope, and raw-token status

## Phase 4B — Okta / OIDC Integration Planning Gate

Status: Implemented

Goal: Map the local pattern to a real enterprise identity provider without introducing secrets or tenant-specific values.

Deliverables:

- Okta/OIDC integration planning document
- OAuth token exchange mapping document
- Production hardening checklist
- OIDC claim mapping plan
- External token exchange boundary plan
- No-secret integration gate

Core controls:

- Local deterministic proof remains the source of truth
- External identity is validated before policy evaluation
- Token exchange is attempted only after policy `ALLOW`
- Downstream API validation remains mandatory
- Raw tokens and client secrets are never committed

## Phase 5 — External Token Validation and Enterprise Hardening

Status: Next

Goal: Add implementation code for external token validation and hardened broker interfaces after the planning gate is complete.

Deliverables:

- External JWT/OIDC validation module
- OIDC claim-to-policy identity mapper
- Optional external OAuth token exchange broker interface
- Sample non-secret OIDC claim payloads
- Tests for issuer, audience, expiration, group mapping, and fail-closed behavior
- No committed tenant secrets

## Recommended Build Order

1. Keep Phase 0 documentation locked before coding.
2. Implement the policy decision loop first.
3. Add token broker only after allow/deny behavior is tested.
4. Add mock APIs after token shape is stable.
5. Add local demo runner before external IdP integration.
6. Add evidence review before external IdP integration.
7. Add OIDC/token-exchange planning before live IdP configuration.
8. Add external validation code only after the integration gate is documented.

This prevents the lab from turning into an identity-provider configuration exercise before the agent security pattern is proven.
