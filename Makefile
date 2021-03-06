# -----------------------------------------------------------------------------
# Copyright 2012-2017 Andreas Maier. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# -----------------------------------------------------------------------------

# Makefile for ownmoviedb project
#
# Basic prerequisites for running this Makefile, to be provided manually:
#   One of these OS platforms:
#     Windows with CygWin
#     Linux (any distro)
#     OS-X
#   These commands on all OS platforms:
#     make (GNU make)
#     bash
#     rm, mv, find, tee, which
#   These commands on all OS platforms in the active Python environment:
#     python (or python3 on OS-X)
#     twine
#   These commands on Linux and OS-X:
#     uname
# OS-level packages:
#   Ubuntu:
#     libmysqlclient-dev
#   OS-X:
#     mysql (or mysql-client + setting various env vars)
# Environment variables:
#   PYTHON_CMD: Python command to use (OS-X needs to distinguish Python 2/3)
#   PIP_CMD: Pip command to use (OS-X needs to distinguish Python 2/3)
#   PACKAGE_LEVEL: minimum/latest - Level of Python dependent packages to use
# Additional prerequisites for running this Makefile are installed by running:
#   make develop

# Python / Pip commands
ifndef PYTHON_CMD
  PYTHON_CMD := python
endif
ifndef PIP_CMD
  PIP_CMD := pip
endif

# Package level
ifndef PACKAGE_LEVEL
  PACKAGE_LEVEL := latest
endif
ifeq ($(PACKAGE_LEVEL),minimum)
  pip_level_opts := -c minimum-constraints.txt
else
  ifeq ($(PACKAGE_LEVEL),latest)
    pip_level_opts := --upgrade
  else
    $(error Error: Invalid value for PACKAGE_LEVEL variable: $(PACKAGE_LEVEL))
  endif
endif

# Determine OS platform make runs on
ifeq ($(OS),Windows_NT)
  PLATFORM := Windows
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

# Make variables are case sensitive and some native Windows environments have
# ComSpec set instead of COMSPEC.
ifndef COMSPEC
  ifdef ComSpec
    COMSPEC = $(ComSpec)
  endif
endif

# Determine OS platform make runs on.
ifeq ($(OS),Windows_NT)
  ifdef PWD
    PLATFORM := Windows_UNIX
  else
    PLATFORM := Windows_native
    ifdef COMSPEC
      SHELL := $(subst \,/,$(COMSPEC))
    else
      SHELL := cmd.exe
    endif
    .SHELLFLAGS := /c
  endif
else
  # Values: Linux, Darwin
  PLATFORM := $(shell uname -s)
endif

ifeq ($(PLATFORM),Windows_native)
  # Note: The substituted backslashes must be doubled.
  # Remove files (blank-separated list of wildcard path specs)
  RM_FUNC = del /f /q $(subst /,\\,$(1))
  # Remove files recursively (single wildcard path spec)
  RM_R_FUNC = del /f /q /s $(subst /,\\,$(1))
  # Remove directories (blank-separated list of wildcard path specs)
  RMDIR_FUNC = rmdir /q /s $(subst /,\\,$(1))
  # Remove directories recursively (single wildcard path spec)
  RMDIR_R_FUNC = rmdir /q /s $(subst /,\\,$(1))
  # Copy a file, preserving the modified date
  CP_FUNC = copy /y $(subst /,\\,$(1)) $(subst /,\\,$(2))
  ENV = set
  WHICH = where
else
  RM_FUNC = rm -f $(1)
  RM_R_FUNC = find . -type f -name '$(1)' -delete
  RMDIR_FUNC = rm -rf $(1)
  RMDIR_R_FUNC = find . -type d -name '$(1)' | xargs -n 1 rm -rf
  CP_FUNC = cp -r $(1) $(2)
  ENV = env | sort
  WHICH = which
endif

# Name of this Python package (top-level Python namespace + Pypi package name)
package_name := ownmoviedb

# Package version (full version, including any pre-release suffixes, e.g. "0.1.0.dev1").
package_version := $(shell $(PYTHON_CMD) setup.py --version)

# Python full version
python_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('{}.{}.{}'.format(*sys.version_info))")

# Python major version
python_major_version := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('{}'.format(sys.version_info[0]))")

# Python major+minor version for use in file names
python_version_fn := $(shell $(PYTHON_CMD) -c "import sys; sys.stdout.write('{}.{}'.format(*sys.version_info[0:2]))")

# Directory for the generated distribution files
dist_dir := dist

# Distribution archives (as built by setup.py)
bdist_file := $(dist_dir)/$(package_name)-$(package_version)-py2.py3-none-any.whl

dist_files := $(bdist_file)

# Source files in the packages
package_py_files := \
    $(wildcard $(package_name)/*.py) \
    $(wildcard $(package_name)/*/*.py) \

# Directory for generated API documentation
doc_build_dir := build_doc

# Directory where Sphinx conf.py is located
doc_conf_dir := docs

# Documentation generator command
doc_cmd := sphinx-build
doc_opts := -v -d $(doc_build_dir)/doctrees -c $(doc_conf_dir) .

# Dependents for Sphinx documentation build
doc_dependent_files := \
    $(doc_conf_dir)/conf.py \
    $(wildcard $(doc_conf_dir)/*.rst) \
    $(package_py_files) \

# Directory with test source files
test_dir := tests

# Test log
test_log_file := test_$(python_version_fn).log

# Source files with test code
test_py_files := \
    $(wildcard $(test_dir)/*.py) \
    $(wildcard $(test_dir)/*/*.py) \
    $(wildcard $(test_dir)/*/*/*.py) \

# Flake8 config file
flake8_rc_file := .flake8

# PyLint config file
pylint_rc_file := .pylintrc

# Source files for check (with PyLint and Flake8)
check_py_files := \
    setup.py \
    $(package_py_files) \
    $(test_py_files) \

ifdef TESTCASES
pytest_opts := -k $(TESTCASES)
else
pytest_opts :=
endif

# Files the distribution archive depends upon.
dist_dependent_files := \
    setup.py \
    README.rst \
    requirements.txt \
    $(wildcard *.py) \
    $(package_py_files) \

# No built-in rules needed:
.SUFFIXES:

.PHONY: help
help:
	@echo 'Makefile for $(package_name) project'
	@echo 'Package version will be: $(package_version)'
	@echo 'Uses the currently active Python environment: Python $(python_version_fn)'
	@echo 'Valid targets are (they do just what is stated, i.e. no automatic prereq targets):'
	@echo '  install    - Install package in active Python environment'
	@echo '  develop    - Prepare the development environment by installing prerequisites'
	@echo '  check      - Run Flake8 on sources and save results in: flake8.log'
	@echo '  pylint     - Run PyLint on sources and save results in: pylint.log'
	@echo '  test       - Run tests (and test coverage) and save results in: $(test_log_file)'
	@echo '               Does not include install but depends on it, so make sure install is current.'
	@echo '               Env.var TESTCASES can be used to specify a py.test expression for its -k option'
	@echo '  build      - Build the distribution files in: $(dist_dir)'
	@echo '               On Linux + OSX, builds: $(bdist_file)'
	@echo '  builddoc   - Build documentation in: $(doc_build_dir)'
	@echo '  all        - Do all of the above'
	@echo '  uninstall  - Uninstall package from active Python environment'
	@echo '  upload     - Upload the distribution files to PyPI (includes uninstall+build)'
	@echo '  clean      - Remove any temporary files'
	@echo '  clobber    - Remove any build products (includes uninstall+clean)'
	@echo "  platform   - Display the information about the platform as seen by make"
	@echo 'Environment variables:'
	@echo '  PACKAGE_LEVEL="minimum" - Install minimum version of dependent Python packages'
	@echo '  PACKAGE_LEVEL="latest" - Default: Install latest version of dependent Python packages'
	@echo '  PYTHON_CMD=... - Name of python command. Default: python'
	@echo '  PIP_CMD=... - Name of pip command. Default: pip'
	@echo '  TESTCASES=... - Set testcases to run (will be used with -k option of py.test)'

.PHONY: platform
platform:
	@echo "makefile: Platform related information as seen by make:"
	@echo "Platform: $(PLATFORM)"
	@echo "Shell used for commands: $(SHELL)"
	@echo "Shell flags: $(.SHELLFLAGS)"
	@echo "Make command location: $(MAKE)"
	@echo "Make version: $(MAKE_VERSION)"
	@echo "Python command name: $(PYTHON_CMD)"
	@echo "Python command location: $(shell $(WHICH) $(PYTHON_CMD))"
	@echo "Python version: $(python_version)"
	@echo "Pip command name: $(PIP_CMD)"
	@echo "Pip command location: $(shell $(WHICH) $(PIP_CMD))"
	@echo "$(package_name) package version: $(package_version)"

.PHONY: all
all: install develop check pylint test build builddoc
	@echo '$@ done.'

.PHONY: _pip
_pip:
	@echo 'Installing/upgrading pip, setuptools, and wheel with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install $(pip_level_opts) pip setuptools wheel

.PHONY: develop
develop: _pip dev-requirements.txt requirements.txt
	@echo 'Installing runtime and development requirements with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install $(pip_level_opts) -r dev-requirements.txt
	@echo '$@ done.'

.PHONY: install
install: _pip requirements.txt setup.py $(package_py_files)
	@echo 'Installing runtime requirements with PACKAGE_LEVEL=$(PACKAGE_LEVEL)'
	$(PIP_CMD) install $(pip_level_opts) -r requirements.txt .
	$(PYTHON_CMD) -c "import $(package_name); print('Import: ok')"
	@echo 'Done: Installed $(package_name) into current Python environment.'
	@echo '$@ done.'

.PHONY: uninstall
uninstall:
	bash -c '$(PIP_CMD) show $(package_name) >/dev/null; rc=$$?; if [[ $$rc == 0 ]]; then $(PIP_CMD) uninstall -y $(package_name); fi'
	@echo '$@ done.'

.PHONY: check
check: flake8.log
	@echo '$@ done.'

.PHONY: pylint
pylint: pylint.log
	@echo '$@ done.'

.PHONY: test
test: $(test_log_file)
	@echo '$@ done.'

.PHONY: build
build: $(dist_files)
	@echo '$@ done.'

.PHONY: builddoc
#builddoc: html
#	@echo '$@ done.'
builddoc:
	@echo 'Warning: $@ disabled for now.'

.PHONY: upload
upload: uninstall $(dist_files)
ifeq (,$(findstring .dev,$(package_version)))
	@echo '==> This will upload $(package_name) version $(package_version) to PyPI!'
	@echo -n '==> Continue? [yN] '
	@bash -c 'read answer; if [[ "$$answer" != "y" ]]; then echo "Aborted."; false; fi'
	twine upload $(dist_files)
	@echo 'Done: Uploaded $(package_name) version to PyPI: $(package_version)'
	@echo '$@ done.'
else
	@echo 'Error: A development version $(package_version) of $(package_name) cannot be uploaded to PyPI!'
	@false
endif

.PHONY: clobber
clobber: uninstall clean
	rm -Rf $(doc_build_dir) htmlcov .tox
	rm -f pylint.log flake8.log test_*.log $(bdist_file) $(sdist_file) $(win64_dist_file)
	@echo 'Done: Removed all build products to get to a fresh state.'
	@echo '$@ done.'

.PHONY: clean
clean:
	rm -Rf build .cache $(package_name).egg-info .eggs
	rm -f MANIFEST MANIFEST.in AUTHORS ChangeLog .coverage
	find . -name "*.pyc" -delete -o -name "__pycache__" -delete -o -name "*.tmp" -delete -o -name "tmp_*" -delete
	@echo 'Done: Cleaned out all temporary files.'
	@echo '$@ done.'

.PHONY: html
html: $(doc_build_dir)/html/docs/index.html
	@echo '$@ done.'

$(doc_build_dir)/html/docs/index.html: Makefile $(doc_dependent_files)
	rm -fv $@
	$(doc_cmd) -b html $(doc_opts) $(doc_build_dir)/html
	@echo "Done: Created the HTML pages with top level file: $@"

.PHONY: pdf
pdf: Makefile $(doc_dependent_files)
	rm -fv $@
	$(doc_cmd) -b latex $(doc_opts) $(doc_build_dir)/pdf
	@echo "Running LaTeX files through pdflatex..."
	$(MAKE) -C $(doc_build_dir)/pdf all-pdf
	@echo "Done: Created the PDF files in: $(doc_build_dir)/pdf/"
	@echo '$@ done.'

.PHONY: man
man: Makefile $(doc_dependent_files)
	rm -fv $@
	$(doc_cmd) -b man $(doc_opts) $(doc_build_dir)/man
	@echo "Done: Created the manual pages in: $(doc_build_dir)/man/"
	@echo '$@ done.'

.PHONY: docchanges
docchanges:
	$(doc_cmd) -b changes $(doc_opts) $(doc_build_dir)/changes
	@echo
	@echo "Done: Created the doc changes overview file in: $(doc_build_dir)/changes/"
	@echo '$@ done.'

.PHONY: doclinkcheck
doclinkcheck:
	$(doc_cmd) -b linkcheck $(doc_opts) $(doc_build_dir)/linkcheck
	@echo
	@echo "Done: Look for any errors in the above output or in: $(doc_build_dir)/linkcheck/output.txt"
	@echo '$@ done.'

.PHONY: doccoverage
doccoverage:
	$(doc_cmd) -b coverage $(doc_opts) $(doc_build_dir)/coverage
	@echo "Done: Created the doc coverage results in: $(doc_build_dir)/coverage/python.txt"
	@echo '$@ done.'

$(bdist_file): Makefile $(dist_dependent_files)
ifneq ($(PLATFORM),Windows)
	rm -Rfv $(package_name).egg-info .eggs build
	$(PYTHON_CMD) setup.py bdist_wheel -d $(dist_dir) --universal
	@echo 'Done: Created binary distribution archive: $@'
else
	@echo 'Error: Creating binary distribution archive requires to run on Linux or OSX'
	@false
endif

pylint.log: Makefile $(pylint_rc_file) $(check_py_files)
ifeq ($(python_major_version), 2)
	rm -fv $@
	-bash -c 'set -o pipefail; pylint --rcfile=$(pylint_rc_file) --output-format=text $(check_py_files) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created PyLint log file: $@'
else
	@echo 'Info: PyLint requires Python 2; skipping this step on Python $(python_major_version)'
endif

flake8.log: Makefile $(flake8_rc_file) $(check_py_files)
	rm -fv $@
	bash -c 'set -o pipefail; flake8 $(check_py_files) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created Flake8 log file: $@'

$(test_log_file): Makefile $(package__py_files) $(test_py_files) .coveragerc
	rm -fv $@
	bash -c 'set -o pipefail; PYTHONWARNINGS=default py.test -s $(test_dir) --cov $(package_name) --cov-config .coveragerc --cov-report=html $(pytest_opts) 2>&1 |tee $@.tmp'
	mv -f $@.tmp $@
	@echo 'Done: Created test log file: $@'
