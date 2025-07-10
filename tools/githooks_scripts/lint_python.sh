#!/bin/sh

set -e

echo "Installing latest dependencies..."
python -m pip install -r requirements/testing/requirements.txt
python -m pip install -r requirements/example_app/requirements.txt

echo "Running ruff in src"
python -m ruff format src

echo "Running black in src"
python -m black src