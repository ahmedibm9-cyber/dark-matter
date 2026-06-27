.PHONY: install test lint typecheck clean format precommit

install:
	pip install -e .
	pip install pytest ruff mypy pre-commit

test:
	python -m pytest src/ -v

lint:
	ruff check src/
	ruff format --check src/

typecheck:
	mypy src/

format:
	ruff format src/

clean:
	rm -rf build/ dist/ *.egg-info
	find . -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -name '*.pyc' -delete

precommit:
	pre-commit run --all-files

all: install test lint typecheck
