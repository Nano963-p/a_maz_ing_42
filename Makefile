# Makefile pour A-Maze-ing Project
# --------------------------------

# Variables
PYTHON = python3
PIP = pip3
MAIN = a_maze_ing.py
CONFIG = config.txt

# Installation des dépendances
install:
	$(PIP) install -r requirements.txt

# Exécution du programme principal
run:
	$(PYTHON) $(MAIN) $(CONFIG)

# Exécution en mode debug avec pdb
debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

# Nettoyage des fichiers temporaires et caches
clean:
	rm -rf __pycache__ .mypy_cache *.pyc

# Linting et vérification statique du code
lint:
	flake8 . --max-line-length=88
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
          --disallow-untyped-defs --check-untyped-defs

# Linting strict (optionnel)
lint-strict:
	flake8 . --max-line-length=88 --strict
	mypy . --strict
