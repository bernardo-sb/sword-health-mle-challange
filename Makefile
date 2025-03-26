

.ONESHELL:
venv:
	uv venv --python 3.11
	uv pip install --upgrade pip setuptools wheel pipenv
	uv pip install -e .

.ONESHELL:
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

.PHONY: zip-project
zip-project:
	git archive --format=zip -o ml-engineer-test_bernardo-lemos.zip HEAD
