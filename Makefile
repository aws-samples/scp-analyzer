help: 
	@cat Makefile

prep:
	poetry config virtualenvs.path .venv && \
	poetry install

clean:
	rm -r .venv/

dev: prep
	poetry run jupyter-lab

install: 
	pip install --user .


