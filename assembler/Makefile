.PHONY: all
all: regression

.PHONY: regression
regression: test

.PHONY: clean
clean:
	rm -rf venv

.PHONY: test
test: venv
	venv/bin/python3 -m pytest

venv:
	python3 -m venv venv
	venv/bin/python3 -m pip install -r requirements.txt
