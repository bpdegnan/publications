#!/bin/sh
set -eu

VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    python -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1091
. "$VENV_DIR/bin/activate"

python -m pip install --upgrade pip
python -m pip install matplotlib
python -m pip install scipy
python -m pip install numpy

echo
echo "Virtual environment ready."
echo "To activate it later, run:"
echo "  source $VENV_DIR/bin/activate"

