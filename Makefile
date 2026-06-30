.PHONY: install test validate demo evidence

install:
	python -m pip install -e .[dev]

test:
	pytest -q

validate: test
	@echo "Validation complete: brokered delegation policy tests passed."

demo:
	python scripts/run_demo.py samples/requests/allow-ticket-create.json

evidence:
	python scripts/show_latest_evidence.py
