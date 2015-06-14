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
	! grep -o '<td>[0-9.]*% imprecise' mypy-report/index.html | grep -v '<td>0.0% imprecise'

.PHONY: coverage
all: coverage
coverage: prep
	${PYTHON} -m pytest -v --cov lr/ --cov-report=html lr/
	! grep "<td class='right'>" htmlcov/index.html | grep -v 100%
