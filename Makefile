# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

help: 
	@cat Makefile

prep:
	poetry config virtualenvs.in-project true && \
	poetry install

clean:
	rm -r .venv/

install: 
	pip install --user .


