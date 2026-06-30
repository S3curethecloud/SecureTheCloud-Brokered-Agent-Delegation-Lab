# Agent Capability Model

## Purpose

The agent capability model defines what an agent is approved to do before it can request delegated access.

The human user may have a permission, but the agent must also be approved for the corresponding tool/action.

This creates dual authorization:

```text
User must be allowed.
Agent must be allowed.
Target app must be allowed.
Requested action must be allowed.
Requested scope must be allowed.
```

## Capability Manifest Example

```yaml
agents:
  - agent_id: support-agent-001
    name: Customer Support Delegation Agent
    allowed_tools:
      - crm.read_customer
      - ticketing.create_ticket
      - knowledge.read_runbook
    denied_tools:
      - hr.read_salary
      - billing.update_payment
      - admin.grant_role
    max_risk_tier: medium
    requires_user_delegation: true
    token_ttl_seconds: 300
```

## Authorization Matrix

| User Permission | Agent Capability | Result |
|---|---|---|
| Yes | Yes | `ALLOW` if all other controls pass |
| Yes | No | `DENY` |
| No | Yes | `DENY` |
| No | No | `DENY` |

## Why This Matters

Agents should not inherit every permission a human user has.

For example, a manager may have permission to view some HR records, but a customer support agent should not automatically inherit that HR access just because the manager triggered it.

The agent capability manifest defines the agent's approved operating envelope.

## Required Fields

| Field | Description |
|---|---|
| `agent_id` | Stable unique agent identifier. |
| `name` | Human readable agent name. |
| `allowed_tools` | Tool/action IDs the agent can request. |
| `denied_tools` | Explicitly prohibited tools/actions. |
| `max_risk_tier` | Maximum risk tier the agent can handle. |
| `requires_user_delegation` | Must be true for this lab. |
| `token_ttl_seconds` | Maximum token lifetime for delegated access. |

## Design Rule

The capability manifest is not optional. If an agent is not registered, it is denied by default.
