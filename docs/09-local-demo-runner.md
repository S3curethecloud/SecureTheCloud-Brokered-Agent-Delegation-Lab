# Phase 4A: Local Demo Runner and Evidence Output

## Purpose

Phase 4A makes the lab demo-friendly.

Instead of only running unit tests, an operator can now execute a sample request and generate a concrete evidence JSON artifact that shows the full brokered delegation chain.

## Demo Flow

```text
sample request
  -> policy decision
  -> token exchange
  -> enterprise API validation
  -> evidence JSON written to evidence/runs/
```

## CLI Usage

Run the default demo through Make:

```bash
make demo
```

Or run the script directly:

```bash
python scripts/run_demo.py samples/requests/allow-ticket-create.json
```

The script prints a concise summary:

```json
{
  "api_access": "SUCCESS",
  "api_authorization_decision": "ALLOW",
  "evidence_path": "evidence/runs/sample-allow-ticket-create-<run-id>.json",
  "policy_decision": "ALLOW",
  "request_id": "sample-allow-ticket-create",
  "token_exchange": "SUCCESS"
}
```

## Evidence Output

Evidence files are written to:

```text
evidence/runs/
```

Generated evidence includes:

- `demo_phase`
- `demo_run_id`
- `request_id`
- `user`
- `agent`
- `target_app`
- `action`
- `requested_scope`
- `policy_decision`
- `token_exchange`
- `token_audience`
- `token_scope`
- `token_ttl_seconds`
- `token_jti`
- `api_access`
- `api_authorization_decision`
- `api_reason_code`
- `raw_token_logged`

## Security Note

The demo runner records token metadata only.

It does not write raw bearer tokens, secrets, or client credentials into evidence output.

## Successful Demo Path

The included sample request is:

```text
samples/requests/allow-ticket-create.json
```

It demonstrates:

1. Alice is authorized for `ticket:create`.
2. The support agent is allowed to perform `ticketing.create_ticket`.
3. The token broker issues a delegated token for `ticketing-api`.
4. The Ticketing API validates audience, scope, expiration, and delegation context.
5. Evidence is written to `evidence/runs/`.

## Denied Path

Denied paths are covered in automated tests. For example, when a user lacks `ticket:create`, the runner records:

```json
{
  "policy_decision": "DENY",
  "token_exchange": "NOT_ATTEMPTED",
  "api_access": "NOT_ATTEMPTED",
  "api_reason_code": "TOKEN_NOT_ISSUED"
}
```

## Validation

Run:

```bash
make validate
```

The test suite verifies:

- Successful demo evidence is written.
- Denied policy requests do not receive delegated tokens.
- Denied requests do not call downstream APIs.
- Evidence contains metadata only, not raw token material.
