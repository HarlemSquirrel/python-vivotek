.PHONY: release
release:
	rm -rf dist
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*

.PHONY: test
test:
	python3 -m unittest
	python3 -m pylint libpyvivotek
