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

Status: Implemented

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

## Phase 4 — Optional Okta / External IdP Integration

Status: Next

Goal: Map the local pattern to a real enterprise identity provider.

Deliverables:

- Okta setup guide
- OIDC app configuration notes
- Authorization server mapping
- Group/claim mapping
- External JWT validation path
- Token exchange integration notes

Exit criteria:

- The local model can be compared directly to a real IdP delegation pattern.
- No client secrets are committed.
- The local security contract remains the source of truth.

## Phase 5 — Enterprise Hardening

Status: Future

Goal: Add advanced controls and presentation-ready evidence.

Deliverables:

- Rich authorization request model
- Sender-constrained token design notes
- Risk-tier-aware policy
- Dashboard/export format
- Architecture review checklist
- Demo script
- Interview talking points

## Recommended Build Order

1. Keep Phase 0 documentation locked before coding.
2. Implement the policy decision loop first.
3. Add token broker only after allow/deny behavior is tested.
4. Add mock APIs after token shape is stable.
5. Add external IdP integration after local API-side enforcement is proven.

This prevents the lab from turning into an identity-provider configuration exercise before the agent security pattern is proven.
