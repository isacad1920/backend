PYTHON ?= python
PIP ?= $(PYTHON) -m pip
PRISMA ?= prisma

.PHONY: install install-dev prisma-generate migrate lint format test run pre-commit hooks clean

install:
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

install-dev: install
	$(PIP) install -r requirements-test.txt
	$(PIP) install ruff black pre-commit

prisma-generate:
	$(PRISMA) generate

migrate:
	$(PRISMA) migrate dev --name manual_change

lint:
	ruff check .

format:
	ruff check --fix . || true
	ruff format .
	black .
	ruff check .

pre-commit:
	pre-commit install

hooks: pre-commit

test:
	pytest -q

run:
	$(PYTHON) run.py

clean:
	rm -rf .pytest_cache __pycache__ */__pycache__ .mypy_cache
