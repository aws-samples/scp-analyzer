# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

help: 
	@cat Makefile

all: prep check lint

prep:
	poetry config virtualenvs.in-project true && \
	poetry install

lint:
	poetry run black scp_analyzer//

check:
	poetry run safety check
	poetry run bandit -r scp_analyzer//

clean:
	rm -r .venv/

install: 
	pip install --user .


