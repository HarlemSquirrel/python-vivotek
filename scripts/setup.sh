#!/bin/bash
# Setup script for python-vivotek development environment

set -e

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

. .venv/bin/activate

pip install --upgrade pip
pip install -e .[tests]
