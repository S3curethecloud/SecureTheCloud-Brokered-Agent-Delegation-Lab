# Source of Truth: SecureTheCloud Brokered Agent Delegation Lab

## Mission

Build an enterprise-grade lab that proves AI agents can perform cross-application work without receiving broad standing privileges.

The lab demonstrates a secure brokered delegation architecture where every downstream action is constrained by the human user, the agent capability manifest, the target application, the requested scope, and policy-as-code.

## Core Principle

> The agent must never have more power than the human user who triggered it.

## What This Lab Is

This is a security architecture and implementation lab for cross-app AI agent access. It models how an agent should safely act as an intermediary between enterprise systems such as CRM, ticketing, knowledge, HR, and other internal APIs.

The first version is intentionally deterministic and local-first. It will simulate identity, policy, token exchange, delegated tokens, and enterprise APIs before adding optional external IdP integration.

## What This Lab Is Not

This lab is not a chatbot demo.

It is not designed to give an agent a broad API key and let it call everything.

It is not a production Okta deployment guide in Phase 0.

It is not a live customer-data integration.

## Target Architecture Pattern

```text
Human User
  -> App / Client
  -> Agent Gateway
  -> Policy Engine
  -> Token Broker
  -> Scoped Delegated Token
  -> Target Enterprise API
  -> Evidence Ledger
```

## Required Guarantees

1. User identity must be validated before agent action.
2. Agent capability must be checked before token issuance.
3. The target application must match the delegated token audience.
4. The requested scope must not exceed the user's permission.
5. The requested scope must not exceed the agent's approved capability.
6. Policy must deny unknown or ambiguous requests by default.
7. Every decision must produce evidence.
8. Raw tokens must never be logged.
9. Token lifetime must be short.
10. Cross-app token reuse must fail.

## Phase Strategy

### Phase 0: Architecture, SoT, Config, Policy, Evidence

Document and scaffold the lab with clear architecture boundaries.

### Phase 1: Policy Simulation

Implement deterministic allow/deny decisions using local config and policy rules.

### Phase 2: Mock Token Broker

Simulate OAuth 2.0 Token Exchange behavior with signed or structured mock delegated tokens.

### Phase 3: Mock Enterprise APIs

Add CRM, Ticketing, and Knowledge APIs that validate delegated token audience and scope.

### Phase 4: Optional Okta / OIDC Integration

Connect the pattern to real identity provider behavior and external JWT validation.

### Phase 5: Enterprise Hardening

Add richer authorization details, sender-constrained token concepts, evidence dashboards, risk tiers, and policy testing.

## Success Criteria

The lab is successful when it can prove the following:

- A valid user can ask an approved agent to perform an approved action against an approved app.
- The agent receives only the minimum required delegated authority.
- The delegated token cannot be used against the wrong app.
- The agent cannot escalate beyond the user.
- The user cannot delegate actions the agent is not allowed to perform.
- Prompt injection cannot bypass the policy broker.
- Every allow and deny decision is represented in evidence.

## Portfolio Statement

This lab demonstrates enterprise IAM, OAuth/OIDC delegation, AI agent governance, cross-app access security, policy-as-code, and audit-ready evidence design.
