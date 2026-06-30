# Phase 4A.1: Demo Walkthrough and Evidence Review

## Purpose

Phase 4A.1 makes the lab easier to present live.

Phase 4A generated full-chain JSON evidence. Phase 4A.1 adds a clean evidence-review command that turns the latest generated evidence file into an interview-ready summary.

## Recommended Live Demo Flow

Run validation first:

```bash
make validate
```

Generate a new evidence file:

```bash
make demo
```

Review the latest evidence summary:

```bash
make evidence
```

Or run the review script directly:

```bash
python scripts/show_latest_evidence.py
```

## Expected Summary

The evidence review command prints a readable summary like:

```text
SecureTheCloud Brokered Delegation Evidence Summary
========================================================
Request: sample-allow-ticket-create
Policy: ALLOW
Token Exchange: SUCCESS
API Decision: ALLOW
API Access: SUCCESS
User: alice@example.com
Agent: support-agent-001
Target App: ticketing-api
Scope: ticket:create
Token Audience: ticketing-api
API Reason: API_ACCESS_GRANTED
Raw Token Logged: false
Evidence File: evidence/runs/sample-allow-ticket-create-<run-id>.json
```

## What To Say In A Demo

Use this short explanation:

> This request starts with a human user and an AI support agent. The policy engine checks whether the user, agent, app, action, scope, data classification, and risk tier are allowed. Only after policy allows the request does the token broker issue a short-lived delegated token. The downstream Ticketing API then independently validates the token audience, scope, expiration, and delegation context before granting access. The run produces evidence without logging raw token material.

## Demo Control Chain

```text
sample request
  -> policy decision
  -> token exchange
  -> enterprise API validation
  -> evidence JSON
  -> evidence summary
```

## Why This Matters

This shows three important enterprise controls:

1. The agent does not decide its own authority.
2. The delegated token is narrow and audience-bound.
3. The downstream API validates the token independently before granting access.

## Key Evidence Fields

| Field | Meaning |
|---|---|
| `policy_decision` | Whether the request passed the policy engine. |
| `token_exchange` | Whether the broker issued a delegated token. |
| `api_authorization_decision` | Whether the downstream API authorized access. |
| `token_audience` | Which target app the token is valid for. |
| `token_scope` | Which downstream permission was delegated. |
| `api_reason_code` | Why the downstream API allowed or denied access. |
| `raw_token_logged` | Must remain `false`. |

## Operator Commands

```bash
make demo
make evidence
```

## Troubleshooting

If no evidence exists yet, run:

```bash
make demo
```

Then rerun:

```bash
make evidence
```

If validation fails, run:

```bash
pytest -q
```

and inspect the failing test.
