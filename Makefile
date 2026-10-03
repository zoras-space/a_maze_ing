PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

.PHONY: install run debug clean lint lint-strict

install:
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + rm -rf .mypy_cache

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint_strict:
	flake8 .
	mypy . --strict