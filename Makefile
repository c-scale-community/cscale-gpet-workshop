.PHONY: help clean setup test

help:
	@echo "make clean"
	@echo " clean all python build/compilation files and directories"
	@echo "make install"
	@echo " install dependencies in active python environment"
	@echo "make test"
	@echo " install dependencies for tests in active python environment if necessary and run test with coverage"
	@echo "make version"
	@echo " update _version.py with current version tag"
	@echo "make dist"
	@echo " build the package ready for distribution and update the version tag"

clean:
	find . -name '*.pyc' -exec rm --force {} +
	find . -name '*.pyo' -exec rm --force {} +
	find . -name '*~' -exec rm --force {} +
	rm --force .coverage
	rm --force --recursive .pytest_cache
	rm --force --recursive build/
	rm --force --recursive dist/
	rm --force --recursive *.egg-info
	rm --force .install.done
	rm --force .install.test.done

install:
	pip install --upgrade pip setuptools
	pip install -e .

.install.test.done:
	pip install --upgrade pip setuptools
	pip install -e .[test]
	touch .install.test.done

test: .install.test.done
	pytest -rsx --verbose --color=yes --cov=cscale_gpet_workshop --cov-report term-missing

version:
	echo "__version__ = \"$(shell git describe --always --tags --abbrev=0)\"\n__commit__ = \"$(shell git rev-parse --short HEAD)\"" > src/cscale_gpet_workshop/_version.py

dist: version
	pip3 install build twine
	python3 -m build
