# Policy Decision Model

## Purpose

The policy decision model defines how the lab determines whether an agent-mediated action should be allowed or denied.

The policy engine evaluates a normalized authorization request.

## Normalized Authorization Request

```json
{
  "request_id": "req-1001",
  "user": "alice@example.com",
  "agent": "support-agent-001",
  "target_app": "ticketing-api",
  "action": "ticketing.create_ticket",
  "requested_scope": "ticket:create",
  "data_classification": "internal",
  "risk_tier": "medium"
}
```

## Required Evaluation Checks

| Check | Description |
|---|---|
| User exists | The user must be known or externally validated. |
| Agent exists | The agent must be registered. |
| App exists | The target app must be registered. |
| Scope exists | The requested scope must be known. |
| User has scope | The user must be allowed to request the scope. |
| Agent has tool | The agent must be allowed to perform the action. |
| App accepts scope | The target app must support the requested scope. |
| Data class allowed | User and agent must be allowed for the data classification. |
| Risk tier allowed | Request risk must not exceed the agent's max risk tier. |

## Allow Example

```json
{
  "decision": "ALLOW",
  "reason_code": "USER_AND_AGENT_AUTHORIZED",
  "allowed_scope": "ticket:create",
  "token_ttl_seconds": 300
}
```

## Deny Examples

```json
{
  "decision": "DENY",
  "reason_code": "USER_LACKS_SCOPE",
  "message": "The user is not allowed to request salary:read."
}
```

```json
{
  "decision": "DENY",
  "reason_code": "AGENT_LACKS_CAPABILITY",
  "message": "The agent is not approved for hr.read_salary."
}
```

```json
{
  "decision": "DENY",
  "reason_code": "TARGET_APP_DOES_NOT_ACCEPT_SCOPE",
  "message": "The requested scope is not valid for the target app."
}
```

## Deny-by-Default Rule

If the policy engine cannot prove that a request should be allowed, the request is denied.

```text
Unknown user -> DENY
Unknown agent -> DENY
Unknown app -> DENY
Unknown action -> DENY
Unknown scope -> DENY
Ambiguous classification -> DENY
```

## Policy Output Contract

All policy evaluations must return a structured decision object:

```json
{
  "request_id": "req-1001",
  "decision": "ALLOW",
  "reason_code": "USER_AND_AGENT_AUTHORIZED",
  "user": "alice@example.com",
  "agent": "support-agent-001",
  "target_app": "ticketing-api",
  "action": "ticketing.create_ticket",
  "requested_scope": "ticket:create",
  "allowed_scope": "ticket:create",
  "token_ttl_seconds": 300
}
```
