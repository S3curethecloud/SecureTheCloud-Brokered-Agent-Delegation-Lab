# Services Scaffold

This folder will contain the runnable implementation for the brokered delegation lab.

## Planned Services

| Service | Purpose |
|---|---|
| `agent-gateway` | Receives user-triggered agent requests and normalizes actions. |
| `policy-engine` | Evaluates whether the user, agent, target app, action, and scope are allowed. |
| `token-broker` | Issues mock short-lived delegated tokens after policy approval. |
| `crm-api` | Mock enterprise CRM API. |
| `ticketing-api` | Mock enterprise ticketing API. |
| `knowledge-api` | Mock enterprise knowledge/runbook API. |

## Implementation Contract

Services should follow the architecture defined in:

- `docs/01-architecture.md`
- `docs/03-token-exchange-flow.md`
- `docs/05-policy-decision-model.md`
- `docs/06-evidence-model.md`

## Phase 1 Build Target

The first runnable version should implement a local deterministic request flow:

```text
sample request -> policy decision -> evidence record
```

No live IdP or LLM is required in Phase 1.
