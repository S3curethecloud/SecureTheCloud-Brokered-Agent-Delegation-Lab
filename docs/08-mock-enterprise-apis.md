# Phase 3: Mock Enterprise APIs

## Purpose

Phase 3 proves that downstream enterprise systems independently enforce delegated-token constraints.

The agent gateway and token broker are important controls, but they are not the final security boundary. Each enterprise API must validate the delegated token before returning data or performing an action.

## Security Boundary

```text
Agent Gateway -> Token Broker -> Delegated Token -> Enterprise API
```

The enterprise API must verify:

1. Token exists.
2. Token is not expired.
3. Token audience matches the API.
4. Token includes the required scope.
5. Token contains human subject context.
6. Token contains acting agent context.
7. Raw token material is not logged into evidence.

## Implemented Mock APIs

| Mock API | Required Audience | Required Scope | Wrapper Function |
|---|---|---|---|
| CRM API | `crm-api` | `customer:read` | `call_crm_api` |
| Ticketing API | `ticketing-api` | `ticket:create` | `call_ticketing_api` |
| Knowledge API | `knowledge-api` | `runbook:read` | `call_knowledge_api` |

## Enforcement Function

The generic enforcement function is:

```python
validate_api_access(
    token,
    target_app="ticketing-api",
    required_scope="ticket:create",
    now_epoch=1200,
)
```

It returns an `ApiAccessResult` object.

## Allow Example

A valid ticketing token with the correct audience and scope returns:

```json
{
  "api_access": "ALLOW",
  "reason_code": "API_ACCESS_GRANTED",
  "target_app": "ticketing-api",
  "required_scope": "ticket:create",
  "token_audience": "ticketing-api",
  "token_scope": "ticket:create",
  "token_subject": "alice@example.com",
  "token_actor": "support-agent-001",
  "token_expired": false,
  "raw_token_logged": false
}
```

## Deny Examples

### Wrong Audience

A token minted for `knowledge-api` must not work against `ticketing-api`.

```json
{
  "api_access": "DENY",
  "reason_code": "TOKEN_AUDIENCE_MISMATCH"
}
```

### Expired Token

A delegated token must fail after expiration.

```json
{
  "api_access": "DENY",
  "reason_code": "TOKEN_EXPIRED"
}
```

### Insufficient Scope

A token with `ticket:read` must not authorize `ticket:create`.

```json
{
  "api_access": "DENY",
  "reason_code": "TOKEN_SCOPE_INSUFFICIENT"
}
```

### Missing Delegation Context

A delegated agent token must include both the human user and the acting agent.

```json
{
  "api_access": "DENY",
  "reason_code": "DELEGATION_CONTEXT_MISSING"
}
```

## Why This Matters

This phase prevents an anti-pattern where downstream systems blindly trust the agent gateway.

In secure enterprise design, the API must enforce its own resource boundary. A token minted for CRM should not work against Ticketing. A token with read-only scope should not perform a write action. An expired token should not be accepted even if the agent still has a cached copy.

## Phase 3 Exit Criteria

Phase 3 is complete when tests prove:

- Valid ticketing token is accepted by Ticketing API.
- Knowledge API token is rejected by Ticketing API.
- Ticketing token is rejected by Knowledge API.
- Expired token is rejected.
- Token with insufficient scope is rejected.
- Token without `act.sub` is rejected.
- Missing token is rejected.
- Unknown target app is rejected.
