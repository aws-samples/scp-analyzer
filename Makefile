help: 
	@cat Makefile

prep:
	poetry config virtualenvs.in-project true && \
	poetry install

clean:
	rm -r .venv/

install: 
	pip install --user .


