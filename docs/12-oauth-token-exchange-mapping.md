# OAuth Token Exchange Mapping

## Purpose

This document maps the local token broker model to OAuth 2.0 Token Exchange concepts.

The local lab intentionally uses structured mock delegated tokens first. A future external IdP implementation can replace the mock broker with a standards-aligned token exchange flow while preserving the same security contract.

## Local Security Contract

The local broker follows this rule:

```text
No policy approval -> no delegated token.
```

The local issued token contains:

```json
{
  "iss": "securethecloud-token-broker",
  "sub": "alice@example.com",
  "act": {
    "sub": "support-agent-001"
  },
  "aud": "ticketing-api",
  "scope": "ticket:create",
  "delegation_type": "on_behalf_of",
  "iat": 1893456700,
  "exp": 1893457000,
  "jti": "unique-token-id"
}
```

## Standards-Aligned Mapping

| Local Concept | OAuth Token Exchange Concept |
|---|---|
| User identity token/context | `subject_token` |
| Agent identity token/context | `actor_token` or actor claim representation |
| Target app | `audience` or `resource` |
| Requested permission | `scope` |
| Token broker | Authorization server / STS role |
| Delegated token | Issued security token |
| Human subject | `sub` |
| Acting agent | `act` claim |
| API boundary | Resource server validating token claims |

## Token Exchange Request Shape

A future external token exchange request would conceptually include:

```text
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
subject_token=<validated-user-token>
subject_token_type=urn:ietf:params:oauth:token-type:access_token
actor_token=<agent-identity-token-or-assertion>
actor_token_type=<supported-actor-token-type>
audience=ticketing-api
scope=ticket:create
requested_token_type=urn:ietf:params:oauth:token-type:access_token
```

## Required Pre-Exchange Checks

Before requesting an external token exchange, the lab should continue to evaluate local policy:

1. Is the user known or trusted through validated IdP claims?
2. Is the agent registered and enabled?
3. Is the agent approved for the requested action?
4. Is the target app registered?
5. Is the requested scope allowed for the user?
6. Is the requested scope allowed for the agent?
7. Is the data classification allowed?
8. Is the risk tier allowed?

Only after these checks return `ALLOW` should token exchange proceed.

## Delegation vs Impersonation Decision

The lab should prefer delegation semantics for AI agents.

Delegation keeps both identities visible:

```text
sub = human user
act.sub = acting agent
```

This is better for agent governance than pure impersonation because downstream systems can see that the action was performed by an agent acting for a human user.

## Audience and Scope Rules

The issued delegated token must be narrower than the original user authority.

| Rule | Requirement |
|---|---|
| Audience-bound | Token must be valid only for the target API. |
| Scope-limited | Token must contain only approved scope. |
| Short-lived | Token TTL should be minimized. |
| Actor-aware | Token should preserve agent identity. |
| Subject-aware | Token should preserve human user identity. |
| Evidence-ready | Token exchange metadata must be recorded. |

## Downstream API Validation

The target API must independently validate:

- `iss`
- `aud`
- `scope` or `scp`
- `exp`
- `sub`
- `act.sub` or equivalent delegation context

The API must not assume that the gateway performed validation correctly.

## Evidence Mapping

| Evidence Field | External Token Exchange Source |
|---|---|
| `token_exchange` | Token endpoint result. |
| `token_exchange_reason_code` | Success or error code. |
| `token_audience` | Issued token audience. |
| `token_scope` | Issued token scope. |
| `token_ttl_seconds` | `exp - iat`. |
| `token_jti` | Issued token identifier, if present. |
| `raw_token_logged` | Must remain `false`. |

## Deny Conditions

External token exchange must not be attempted when:

- Local policy denies the request.
- User token validation fails.
- Actor/agent identity is missing.
- Requested scope exceeds user authority.
- Requested scope exceeds agent capability.
- Requested target app is unknown.
- Requested audience is not registered.
- Data classification or risk tier is not allowed.

## Future Implementation Notes

When this becomes code, use an interface boundary:

```python
class TokenBroker:
    def exchange(policy_decision, request_context):
        ...
```

Then support two implementations:

```text
MockTokenBroker
ExternalOAuthTokenExchangeBroker
```

This preserves deterministic local tests while allowing external integration to be added without weakening the existing controls.

## References

- RFC 8693 defines OAuth 2.0 Token Exchange and includes delegation and impersonation semantics: https://www.rfc-editor.org/rfc/rfc8693.html
- RFC 8693 defines `subject_token`, `actor_token`, `audience`, `resource`, and `scope` request concepts: https://www.rfc-editor.org/rfc/rfc8693.html
- RFC 9700 provides current OAuth 2.0 security best current practice guidance: https://www.rfc-editor.org/rfc/rfc9700.html
