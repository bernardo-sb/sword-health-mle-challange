

.ONESHELL:
venv:
	uv venv --python 3.11
	uv pip install --upgrade pip setuptools wheel pipenv
	uv pip install -e .

.PHONY: dev
dev:
	uv venv --python 3.11
	uv pip install --upgrade pip setuptools wheel pipenv
	uv pip install -e .[dev]

.PHONY: transform
transform:
	message transform

.PHONY: get-message
get-message:
	message get-message $(session_group)
