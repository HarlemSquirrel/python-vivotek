#!/usr/bin/env python3
"""libpyvivotek setup script."""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='libpyvivotek',
    version='0.4.1',
    description='Python Library for Vivotek IP Cameras',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Kevin McCormack',
    author_email='HarlemSquirrel@gmail.com',
    url='https://github.com/HarlemSquirrel/python-vivotek',
    license='LGPLv3+',
    install_requires=[
        'requests',
    ],
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    keywords=['vivotek', 'Camera', 'IPC'],
    test_suite="tests",
)
