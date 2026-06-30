# Initial Test Plan

## Purpose

This test plan defines the security cases the lab must prove before adding external identity provider integration.

## Phase 1 Policy Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| T001 | Alice uses support agent to create ticket | `ALLOW` |
| T002 | Bob uses support agent to create ticket without `ticket:create` scope | `DENY` |
| T003 | Alice asks support agent to read HR salary data | `DENY` |
| T004 | Unknown agent requests CRM access | `DENY` |
| T005 | Unknown target app is requested | `DENY` |
| T006 | Agent requests `admin:grant_role` | `DENY` |
| T007 | Mallory tries to read confidential customer data | `DENY` |
| T008 | User has permission but agent lacks capability | `DENY` |
| T009 | Agent has capability but user lacks permission | `DENY` |
| T010 | Data classification exceeds user clearance | `DENY` |

## Phase 2 Token Broker Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| T101 | Policy allows ticket creation | Delegated token issued |
| T102 | Policy denies HR salary read | Token exchange not attempted |
| T103 | Token contains human `sub` and agent `act` | Pass |
| T104 | Token audience matches target app | Pass |
| T105 | Token TTL is less than or equal to agent max TTL | Pass |
| T106 | Raw token is not written to evidence | Pass |

## Phase 3 API Enforcement Tests

| Test ID | Scenario | Expected Result |
|---|---|---|
| T201 | CRM receives CRM token with `customer:read` | `ALLOW` |
| T202 | Ticketing receives ticket token with `ticket:create` | `ALLOW` |
| T203 | Ticketing receives CRM audience token | `DENY` |
| T204 | API receives expired token | `DENY` |
| T205 | API receives token without required scope | `DENY` |

## Evidence Validation Tests

Every test should verify that evidence exists and contains:

- `request_id`
- `user`
- `agent`
- `target_app`
- `action`
- `requested_scope`
- `policy_decision`
- `reason_code`
- `token_exchange`
- `api_access`
- `raw_token_logged: false`
