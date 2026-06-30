.PHONY: install test validate

install:
	python -m pip install -e .[dev]

test:
	pytest -q

validate: test
	@echo "Validation complete: brokered delegation policy tests passed."
