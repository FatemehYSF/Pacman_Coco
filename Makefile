VENV    = .venv
PYTHON  = $(VENV)/bin/python
CONFIG  = config.json
MAZE    = mazegenerator-00001-py3-none-any.whl
MYPY    = --warn-return-any --warn-unused-ignores --ignore-missing-imports \
          --disallow-untyped-defs --check-untyped-defs

install:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install --force-reinstall $(MAZE)

run:
	$(PYTHON) pac-man.py $(CONFIG)

debug:
	$(PYTHON) -m pdb pac-man.py $(CONFIG)

clean:
	find . -name __pycache__ -not -path "./$(VENV)/*" -exec rm -rf {} +
	rm -rf .mypy_cache build dist *.spec

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY)

lint-strict:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --strict

package:
	sh package.sh

.PHONY: install run debug clean lint lint-strict package
