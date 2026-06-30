# Phase 4B: Okta / OIDC Integration Plan

## Purpose

This document defines the documentation-first integration gate for mapping the local brokered delegation lab to a real enterprise identity provider.

The goal is not to wire a live Okta tenant yet. The goal is to define the integration contract, claims, trust boundaries, policy mapping, and safety gates before tenant-specific configuration or secrets are introduced.

## Integration Principle

> Local deterministic proof first, external IdP integration second.

The lab has already proven the local security chain:

```text
sample request
  -> policy decision
  -> token exchange
  -> enterprise API validation
  -> evidence JSON
  -> evidence summary
```

Okta/OIDC integration should preserve that same chain, replacing local user simulation with externally validated identity claims.

## Target Integration Pattern

```text
Human User
  -> OIDC Login
  -> User Access Token / ID Context
  -> Agent Gateway
  -> Policy Engine
  -> Token Broker / Token Exchange
  -> Scoped Delegated Token
  -> Enterprise API
  -> Evidence
```

## Non-Goals For This Gate

This phase does not commit:

- Okta client secrets
- Real tenant URLs
- Real authorization server IDs
- Real user or group identifiers
- Production API credentials
- Live token exchange calls
- Live enterprise API calls

## Required OIDC Inputs

The eventual integration should validate and map these identity claims or equivalent values:

| Claim / Field | Purpose |
|---|---|
| `iss` | Trusted issuer / authorization server. |
| `sub` | Stable user subject. |
| `aud` | Intended client or API audience. |
| `exp` | Token expiration. |
| `iat` | Token issued time. |
| `groups` or equivalent | Authorization group mapping. |
| `scp` or `scope` | Granted user scopes. |
| `email` | Human-readable identity for evidence, if available. |

## Local-to-OIDC Mapping

| Local Lab Field | External OIDC / IdP Source |
|---|---|
| `user` | `sub`, `email`, or mapped principal. |
| `roles` | Group or app assignment claims. |
| `allowed_scopes` | Token scopes plus enterprise policy mapping. |
| `clearance` | Group-derived or attribute-derived policy input. |
| `max_risk_tier` | Policy decision derived from group, role, or attribute. |
| `agent` | Registered agent capability manifest. |
| `target_app` | Token exchange `audience` or `resource`. |
| `requested_scope` | Token exchange `scope`. |

## Required Validation Before Policy Evaluation

Before the local policy engine accepts external identity context, the integration must validate:

1. Token issuer is trusted.
2. Token signature is valid.
3. Token is not expired.
4. Token audience is expected.
5. Token subject is present.
6. Token scopes and groups are parsed safely.
7. Unknown groups do not create implicit permissions.
8. Missing attributes fail closed.

## Integration Components

| Component | Responsibility |
|---|---|
| OIDC Provider | Authenticates human user and issues identity/access tokens. |
| Agent Gateway | Receives user context and normalized agent request. |
| Identity Mapper | Converts OIDC claims into local policy input. |
| Policy Engine | Makes deterministic allow/deny decision. |
| Token Broker | Requests or simulates delegated token issuance. |
| Enterprise API | Validates audience, scope, expiration, and delegation context. |
| Evidence Review | Produces human-readable proof of the full chain. |

## Planned Files For Live Integration Phase

Future implementation should be added only after this gate is accepted.

Recommended future files:

```text
src/brokered_delegation/oidc_claims.py
src/brokered_delegation/external_token_validator.py
src/brokered_delegation/identity_mapper.py
tests/test_oidc_claims.py
tests/test_identity_mapper.py
samples/oidc/sample-id-token-claims.json
samples/oidc/sample-access-token-claims.json
```

## Okta Configuration Planning Checklist

Use tenant-specific values only in local `.env` files or secure secret stores.

| Item | Planning Requirement |
|---|---|
| Authorization server | Identify the issuer used for access tokens. |
| OIDC client app | Use Authorization Code + PKCE for user-facing login. |
| API audience | Define target API audiences such as `ticketing-api`. |
| Scopes | Define explicit scopes such as `ticket:create`, `customer:read`, and `runbook:read`. |
| Groups | Map groups to local roles and clearance. |
| Claims | Decide which claims are sent in ID token vs access token. |
| Key discovery | Use JWKS discovery for token validation. |
| Secrets | Never commit client secrets or tenant-specific tokens. |

## Evidence Requirements

When external identity is added, evidence should include metadata such as:

- trusted issuer validation result
- token audience validation result
- user subject
- mapped user principal
- mapped groups or roles
- policy decision
- token exchange outcome
- downstream API decision
- raw token logged flag, always `false`

Evidence must not include raw ID tokens, raw access tokens, refresh tokens, client secrets, or tenant-specific credentials.

## Gate Exit Criteria

Phase 4B planning is complete when:

- The OIDC/OAuth mapping is documented.
- The local-to-external identity mapping is clear.
- The token exchange mapping is documented.
- The production hardening checklist is documented.
- No secrets or tenant-specific values are committed.
- The deterministic local lab remains fully validated.

## References

- RFC 8693: OAuth 2.0 Token Exchange — https://www.rfc-editor.org/rfc/rfc8693.html
- OpenID Connect Core 1.0 — https://openid.net/specs/openid-connect-core-1_0.html
- RFC 9700: Best Current Practice for OAuth 2.0 Security — https://www.rfc-editor.org/rfc/rfc9700.html
