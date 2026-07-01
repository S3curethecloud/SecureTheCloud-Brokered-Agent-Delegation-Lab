# Samples

This folder contains non-secret sample inputs for the brokered delegation flow.

## Delegation Requests

- `requests/allow-ticket-create.json` — approved support-ticket creation path for the customer support delegation agent.
- `requests/allow-runbook-read.json` — approved knowledge runbook read path for the customer support delegation agent.

## OIDC Claim Samples

- `oidc/sample-access-token-claims.json` — valid non-secret sample claims for Alice.
- `oidc/sample-invalid-token-claims.json` — invalid non-secret claims used for fail-closed validation.

These OIDC samples are not real tokens. They contain no bearer token value, signature, client secret, refresh token, or tenant-specific credential.

## Additional recommended local samples

Create additional request files locally as you test new abuse cases, such as:

- A support analyst attempting a ticket creation action without the required scope.
- An unknown target application request.
- An unknown agent request.
- A privileged action request outside the agent capability manifest.
- A claims object with unknown groups.
- A claims object that lacks the requested scope.

These cases are covered in the test suite.
