PYTHON = python3
PIP = pip3
MAIN = a_maze_ing.py
CONFIG = config.txt


install:
	$(PIP) install -r requirements.txt

run:                                                                                                                                                                        
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -rf .mypy_cache

lint:
	python3 -m flake8 .
	python3 -m  mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs