# Evidence Model

## Purpose

The evidence model records the security decision trail for every agent-mediated access attempt.

Evidence should explain:

- Who triggered the request
- Which agent acted
- Which app was targeted
- Which action and scope were requested
- Whether policy allowed or denied the request
- Whether token exchange occurred
- Whether downstream API access succeeded or failed

## Evidence Principles

1. Evidence must be generated for both `ALLOW` and `DENY` outcomes.
2. Evidence must not contain raw bearer tokens.
3. Evidence must include reason codes.
4. Evidence must be useful for audit, incident response, and architecture review.
5. Evidence must capture token metadata when a delegated token is issued.

## Evidence Record Example

```json
{
  "timestamp": "2026-06-30T12:00:00Z",
  "request_id": "req-1001",
  "user": "alice@example.com",
  "agent": "support-agent-001",
  "target_app": "ticketing-api",
  "action": "ticketing.create_ticket",
  "requested_scope": "ticket:create",
  "data_classification": "internal",
  "risk_tier": "medium",
  "policy_decision": "ALLOW",
  "reason_code": "USER_AND_AGENT_AUTHORIZED",
  "token_exchange": "SUCCESS",
  "token_audience": "ticketing-api",
  "token_scope": "ticket:create",
  "token_ttl_seconds": 300,
  "api_access": "SUCCESS",
  "raw_token_logged": false
}
```

## Deny Evidence Example

```json
{
  "timestamp": "2026-06-30T12:05:00Z",
  "request_id": "req-1002",
  "user": "alice@example.com",
  "agent": "support-agent-001",
  "target_app": "hr-api",
  "action": "hr.read_salary",
  "requested_scope": "salary:read",
  "data_classification": "restricted",
  "risk_tier": "high",
  "policy_decision": "DENY",
  "reason_code": "USER_LACKS_SCOPE_AND_AGENT_LACKS_CAPABILITY",
  "token_exchange": "NOT_ATTEMPTED",
  "api_access": "NOT_ATTEMPTED",
  "raw_token_logged": false
}
```

## Required Evidence Fields

| Field | Required | Description |
|---|---:|---|
| `timestamp` | Yes | UTC timestamp for the decision. |
| `request_id` | Yes | Unique request identifier. |
| `user` | Yes | Human triggering user. |
| `agent` | Yes | Acting agent. |
| `target_app` | Yes | Target enterprise system. |
| `action` | Yes | Normalized action. |
| `requested_scope` | Yes | Requested downstream scope. |
| `policy_decision` | Yes | `ALLOW` or `DENY`. |
| `reason_code` | Yes | Machine-readable reason. |
| `token_exchange` | Yes | `SUCCESS`, `FAILED`, or `NOT_ATTEMPTED`. |
| `api_access` | Yes | `SUCCESS`, `FAILED`, or `NOT_ATTEMPTED`. |
| `raw_token_logged` | Yes | Must be `false`. |

## Evidence Use Cases

- Security architecture reviews
- AI governance reporting
- Incident investigation
- Least-privilege validation
- Audit evidence
- Demo dashboards
- Policy test validation
