# Token Exchange Flow

## Purpose

The token exchange flow models how a user token is converted into a short-lived, audience-bound, scope-limited delegated token for a specific downstream enterprise application.

This lab starts with a mock token broker so the security contract is clear before integrating a real identity provider.

## Delegation Pattern

```text
User Access Token
  -> Policy Decision
  -> Token Broker
  -> Scoped Delegated Token
  -> Target API
```

## Required Inputs

| Input | Description |
|---|---|
| `subject_token` | The user's access token or local user context. |
| `subject` | Human user identity, such as `alice@example.com`. |
| `actor` | Agent identity, such as `support-agent-001`. |
| `audience` | Target downstream API, such as `ticketing-api`. |
| `requested_scope` | Requested permission, such as `ticket:create`. |
| `action` | Normalized action, such as `ticketing.create_ticket`. |
| `policy_decision` | Must be `ALLOW` before token issuance. |

## Mock Delegated Token Claims

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
  "iat": 1893455700,
  "exp": 1893456000,
  "jti": "demo-token-001"
}
```

## Token Rules

1. The broker must not issue a token unless policy returns `ALLOW`.
2. The token audience must match one target app.
3. The token scope must be reduced to the approved scope.
4. The token must be short-lived.
5. The token must preserve both human subject and agent actor.
6. The raw token must not be written to evidence logs.
7. Target APIs must reject tokens with wrong audience or insufficient scope.

## Example Successful Exchange

```json
{
  "request_id": "req-1001",
  "subject": "alice@example.com",
  "actor": "support-agent-001",
  "target_app": "ticketing-api",
  "requested_scope": "ticket:create",
  "policy_decision": "ALLOW",
  "token_exchange": "SUCCESS",
  "issued_audience": "ticketing-api",
  "issued_scope": "ticket:create",
  "ttl_seconds": 300
}
```

## Example Denied Exchange

```json
{
  "request_id": "req-1002",
  "subject": "alice@example.com",
  "actor": "support-agent-001",
  "target_app": "hr-api",
  "requested_scope": "salary:read",
  "policy_decision": "DENY",
  "token_exchange": "NOT_ATTEMPTED",
  "reason": "USER_LACKS_PERMISSION_AND_AGENT_LACKS_CAPABILITY"
}
```

## Real-World Mapping

In a production-grade version, this pattern can map to OAuth 2.0 Token Exchange or an On-Behalf-Of delegation flow.

The important architectural lesson is not the vendor-specific implementation detail. The important lesson is the security invariant:

> The delegated token must be narrower than, and never broader than, the user's original authority.
