.ONESHELL:
SHELL = /bin/bash

.PHONY: help clean environment install test version dist

CONDA_ENV_DIR = $(shell conda info --base)/envs/cscale-gpet-workshop
CONDA_ACTIVATE = source $$(conda info --base)/etc/profile.d/conda.sh ; conda activate ; conda activate

help:
	@echo "make clean"
	@echo " clean all python build/compilation files and directories"
	@echo "make environment"
	@echo " create a conda environment named cscale-gpet-workshop with some conda-forge / nvidia dependencies installed"
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

$(CONDA_ENV_DIR):
	@echo "creating new base cscale-gpet-workshop conda environment..."
	conda create -y -c conda-forge -c nvidia -n cscale-gpet-workshop python=3.10 pip mamba
	$(CONDA_ACTIVATE) cscale-gpet-workshop
	mamba install -y -c conda-forge -c nvidia gdal xarray numpy rioxarray dask numba cudatoolkit
	@echo "... finished."

environment: $(CONDA_ENV_DIR)
	@echo -e "conda environment is ready. To activate use:\n\tconda activate cscale-gpet-workshop"

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
