# Threat Model

## Scope

This threat model covers the brokered delegation pattern for AI agents that perform cross-app access on behalf of enterprise users.

## Protected Assets

| Asset | Why It Matters |
|---|---|
| User identity context | Determines what the agent may do on behalf of the user. |
| Delegated tokens | Grant scoped downstream access to enterprise APIs. |
| Agent capability manifest | Defines the agent's approved tool/action boundary. |
| Policy decision records | Explain why a request was allowed or denied. |
| Enterprise API data | Includes customer, support, knowledge, or sensitive business records. |
| Evidence ledger | Provides audit, investigation, and governance proof. |

## Trust Assumptions

1. The user authenticates through an approved identity provider or local simulation.
2. The agent gateway is the only approved path for delegated agent actions.
3. The policy engine is authoritative for allow/deny decisions.
4. The token broker does not mint delegated tokens without policy approval.
5. Target APIs validate audience, expiration, and scope.
6. Evidence records do not contain raw access tokens.

## Threats and Controls

| Threat | Example | Control |
|---|---|---|
| Prompt injection | User content tells the agent to read HR salary data. | Tool/action is policy checked before execution. |
| Scope escalation | Agent requests `admin:*` instead of `ticket:create`. | Requested scope must be allowed for user and agent. |
| Cross-app token replay | CRM token is used against Ticketing API. | Target API checks `aud`. |
| Overprivileged service account | Agent uses static admin key. | Agent only receives delegated short-lived token. |
| Token leakage in logs | Raw bearer token appears in evidence. | Evidence stores token metadata, not token value. |
| User-agent mismatch | Agent tries to act without a triggering user. | `sub` and `act` claims must be present. |
| Unknown target app | Agent asks to call an unregistered API. | Deny by default for unknown apps. |
| Unknown action | Agent calls a tool not in its manifest. | Agent capability manifest denies unapproved tools. |
| Data classification bypass | Agent requests restricted data with ordinary scope. | Policy checks target data class and risk tier. |

## STRIDE Mapping

| STRIDE Category | Lab Concern | Control |
|---|---|---|
| Spoofing | Fake user or fake agent identity | Validate user and agent identity fields. |
| Tampering | Modified requested scope or audience | Policy decision binds action, scope, and app. |
| Repudiation | No proof of who triggered access | Evidence records user, agent, action, and decision. |
| Information Disclosure | Agent accesses restricted data | Data classification and scope policy. |
| Denial of Service | Agent loops or repeatedly requests tokens | Future rate limiting and quota controls. |
| Elevation of Privilege | Agent exceeds user authority | Scope reduction and dual authorization. |

## Required Deny Cases

The lab must deny:

- Agent has no registered capability.
- User has no permission for requested scope.
- Target app is unknown.
- Requested scope is unknown.
- Data classification exceeds user clearance.
- Token audience does not match target app.
- Token is expired.
- Request lacks human user context.
- Prompt injection asks for unrelated sensitive access.

## Evidence Requirements

Every decision must capture:

- Timestamp
- Request ID
- User
- Agent
- Target app
- Action
- Requested scope
- Decision
- Reason code
- Token exchange result, if applicable
- Token audience, if applicable
- Token TTL, if applicable
- Raw token logged flag, expected to be false

## Out of Scope for Phase 0

- Real Okta tenant configuration
- Real production OAuth client secrets
- Live customer or HR data
- Production-grade key management
- Full SIEM integration
- Runtime LLM tool execution

These can be added in later phases after the deterministic security contract is stable.
