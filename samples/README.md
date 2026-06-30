# Sample Requests

This folder contains example JSON authorization requests for the brokered delegation flow.

## Included

- `requests/allow-ticket-create.json` — approved support-ticket creation path for the customer support delegation agent.

## Additional recommended local samples

Create additional request files locally as you test new abuse cases, such as:

- A support analyst attempting a ticket creation action without the required scope.
- An unknown target application request.
- An unknown agent request.
- A privileged action request outside the agent capability manifest.

These cases are already covered in `tests/test_policy_engine.py` and `tests/test_token_broker.py`.
