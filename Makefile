PYTHON=python3

E =

.PHONY: prep
all: prep
prep:
	${PYTHON} ./python-3-check.py
	rm -rf htmlcov/ .coverage

.PHONY: coverage
all: coverage
coverage: prep
	${PYTHON} -m pytest -vv --cov lr/ --cov-report=html --cov-report=xml lr/
	$E ! xmllint coverage.xml --xpath '//*[@line-rate != "1"]/@filename'

.PHONY: test
# deliberately not in all:
test: prep
	${PYTHON} -m pytest lr/
