# Production Hardening Checklist

## Purpose

This checklist defines what must be true before the brokered agent delegation pattern is considered production-ready.

The current lab is intentionally local and deterministic. Production hardening should happen only after the local proof, demo runner, evidence output, and evidence review flow remain stable.

## Identity and OIDC Hardening

| Control | Requirement | Status |
|---|---|---|
| Trusted issuer validation | Accept tokens only from configured trusted issuers. | Planned |
| JWKS validation | Validate JWT signatures using trusted key discovery. | Planned |
| Audience validation | Validate token audience before policy evaluation. | Planned |
| Expiration validation | Reject expired identity and access tokens. | Planned |
| Clock skew handling | Define small accepted clock skew. | Planned |
| Subject mapping | Map `sub` to a stable local principal. | Planned |
| Group mapping | Map groups to roles through explicit allowlists. | Planned |
| Missing claims | Fail closed when required claims are absent. | Planned |

## Agent Identity Hardening

| Control | Requirement | Status |
|---|---|---|
| Agent registry | Every agent must be registered before use. | Implemented locally |
| Agent capability manifest | Agent actions must be explicitly allowed. | Implemented locally |
| Agent versioning | Production agents should have immutable version identifiers. | Planned |
| Agent attestation | Consider signed agent manifests or deployment attestation. | Future |
| Tool allowlist | Agents can call only approved tools. | Implemented locally |
| Disabled agents | Disabled agents must fail closed. | Implemented locally |

## Token Broker Hardening

| Control | Requirement | Status |
|---|---|---|
| Policy-before-exchange | Token exchange is allowed only after policy `ALLOW`. | Implemented locally |
| Short-lived tokens | Delegated tokens should have short TTLs. | Implemented locally |
| Audience-bound tokens | Tokens must target only the intended API. | Implemented locally |
| Scope reduction | Delegated scope must not exceed user or agent authority. | Implemented locally |
| Token identifier | Use `jti` or equivalent token identifier where supported. | Implemented locally |
| Revocation strategy | Define how revocation propagates to delegated tokens. | Planned |
| Raw token logging | Raw tokens must never be logged. | Implemented locally |
| Sender-constrained tokens | Consider DPoP or mTLS-bound tokens for high-risk APIs. | Future |

## Enterprise API Hardening

| Control | Requirement | Status |
|---|---|---|
| API-side validation | APIs independently validate tokens. | Implemented locally |
| Audience validation | APIs reject wrong-audience tokens. | Implemented locally |
| Scope validation | APIs reject insufficient scopes. | Implemented locally |
| Expiration validation | APIs reject expired tokens. | Implemented locally |
| Delegation context validation | APIs require human and agent context. | Implemented locally |
| Per-resource authorization | Resource-level policy should be enforced beyond coarse scopes. | Planned |
| Rate limiting | Apply API rate limits per user, agent, and app. | Planned |
| Replay defense | Add nonce, DPoP, mTLS, or replay detection where required. | Future |

## Evidence and Audit Hardening

| Control | Requirement | Status |
|---|---|---|
| Decision evidence | Every allow/deny produces evidence. | Implemented locally |
| Token exchange metadata | Evidence captures token metadata only. | Implemented locally |
| API access evidence | API decision is included in evidence. | Implemented locally |
| Evidence summary | Latest evidence can be summarized for demos. | Implemented locally |
| Raw token exclusion | Evidence must not contain raw bearer tokens. | Implemented locally |
| Tamper resistance | Production evidence should be append-only or integrity-protected. | Planned |
| Retention policy | Define retention period and access control. | Planned |
| Privacy review | Avoid unnecessary personal data in evidence. | Planned |

## Secret Management Hardening

| Control | Requirement | Status |
|---|---|---|
| No committed secrets | Secrets must never be committed to Git. | Required |
| Local `.env` only | Developer-only values belong in ignored `.env` files. | Required |
| Secret store | Production values belong in a secret manager. | Planned |
| Rotation | Define client secret and key rotation procedures. | Planned |
| Least privilege | Integration credentials must be minimally scoped. | Planned |
| Break-glass | Emergency access must be audited and time-bound. | Future |

## Policy Hardening

| Control | Requirement | Status |
|---|---|---|
| Deny by default | Unknown users, agents, scopes, apps, and APIs fail closed. | Implemented locally |
| Explicit allowlists | Permissions are granted only through explicit configuration. | Implemented locally |
| Classification-aware access | Data classification affects authorization. | Implemented locally |
| Risk-tier checks | Risk tier affects authorization. | Implemented locally |
| Approval workflow | High-risk actions may require approval. | Future |
| Policy testing | Policy decisions must be covered by tests. | Implemented locally |
| Policy change review | Production policy changes require review. | Planned |

## Observability Hardening

| Control | Requirement | Status |
|---|---|---|
| Structured logs | Use structured logs without raw tokens. | Planned |
| Metrics | Track allow, deny, token exchange, and API decision counts. | Future |
| Alerts | Alert on repeated denials or suspicious cross-app attempts. | Future |
| Dashboard | Build an operator dashboard for evidence trends. | Future |
| Traceability | Correlate request ID across policy, broker, API, and evidence. | Implemented locally |

## Readiness Gates

Production implementation should not proceed unless:

1. Local tests pass.
2. Demo evidence is generated successfully.
3. Evidence summary is readable and accurate.
4. OIDC claim mapping is documented.
5. Token exchange mapping is documented.
6. No secrets are committed.
7. Downstream API validation remains mandatory.
8. Raw token logging remains blocked.
9. Fail-closed behavior is preserved.
10. Security review is completed.

## Future Hardening Ideas

- Sender-constrained tokens using DPoP or mTLS.
- Signed agent capability manifests.
- Approval-required decision path for high-risk actions.
- Evidence integrity chain or append-only storage.
- Dashboard for denied attempts and delegated-token issuance.
- SIEM export for policy and API decisions.

## References

- RFC 9700: Best Current Practice for OAuth 2.0 Security — https://www.rfc-editor.org/rfc/rfc9700.html
- RFC 9449: OAuth 2.0 Demonstrating Proof of Possession — https://www.rfc-editor.org/rfc/rfc9449.html
- RFC 8693: OAuth 2.0 Token Exchange — https://www.rfc-editor.org/rfc/rfc8693.html
