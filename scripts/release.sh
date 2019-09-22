#!/bin/bash

##
# Relase script
#
# Build and upload a new release to pypi.org.
#
# See https://packaging.python.org/tutorials/packaging-projects/

# Exit immediately if a command exits with a non-zero status.
set -e

# Build
python3 setup.py sdist bdist_wheel

# Install latest twine
python3 -m pip install --user --upgrade twine

# Check archives
python3 -m twine check dist/*

# Upload archives
python3 -m twine upload dist/*
