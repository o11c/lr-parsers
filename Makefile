PYTHON=python3
MYPY=mypy

E =

.PHONY: prep
all: prep
prep:
	${PYTHON} ./python-3-check.py
	rm -rf htmlcov/ mypy-report/ .coverage
	find lr/ -name 'test_*.py' | sed 's/\.py//;s:/:.:g;s/^/import /' > mypy-hack.py

.PHONY: mypy
all: mypy
mypy: prep
	${MYPY} --html-report mypy-report --xml-report mypy-report ./mypy-hack.py
	$E ! xmllint mypy-report/index.xml --xpath '/mypy-report-index/file[@imprecise != "0" or @any != "0"]/@name'

.PHONY: coverage
all: coverage
coverage: prep
	${PYTHON} -m pytest -vv --cov lr/ --cov-report=html --cov-report=xml lr/
	$E ! xmllint coverage.xml --xpath '//*[@line-rate != "1"]/@filename'

.PHONY: test
# deliberately not in all:
test: prep
	${PYTHON} -m pytest lr/
