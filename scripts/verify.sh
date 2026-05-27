#!/bin/bash
# Verify script for python-vivotek development environment

set -e

mypy libpyvivotek tests

pylint libpyvivotek tests
