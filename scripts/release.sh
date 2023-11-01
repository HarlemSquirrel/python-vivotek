#!/bin/bash

##
# Relase script
#
# Build and upload a new release to pypi.org.
#
# See https://packaging.python.org/tutorials/packaging-projects/

# Exit immediately if a command exits with a non-zero status.
set -e

# Install latest build
python3 -m pip install --upgrade build

# Build
python3 -m build

# Install latest twine
python3 -m pip install --user --upgrade twine

# Check archives
python3 -m twine check dist/*

# Upload archives
python3 -m twine upload dist/*
