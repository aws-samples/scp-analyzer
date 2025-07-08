# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

help: 
	@cat Makefile

all: prep

prep:
	uv sync 
	uv run pip-audit --local || (uv sync --upgrade && uv run pip-audit --local)
	uv run pip-licenses --output NOTICE
	uv run ruff check --fix 
	uv run ruff format

clean:
	rm -r .venv/

install: 
	pip install --user .


