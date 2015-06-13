PYTHON=python
MYPY=mypy

.PHONY: prep
all: prep
prep:
	${PYTHON} ./python-3-check.py
	rm -rf htmlcov/ mypy-report/ .coverage
	find lr/ -name 'test_*.py' | sed 's/\.py//;s:/:.:g;s/^/import /' > mypy-hack.py

.PHONY: mypy
all: mypy
mypy: prep
	${MYPY} --html-report mypy-report ./mypy-hack.py

.PHONY: coverage
all: coverage
coverage: prep
	${PYTHON} -m pytest -v --cov lr/ --cov-report=html lr/
