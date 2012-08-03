APPNAME=turses
VERSION=0.2.7
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=nosetests
WATCHTESTFLAGS=--verbosity=0


all: turses

turses: clean test dist install

dist: clean
	$(DIST)

install: 
	$(PY) setup.py develop

clean: pyc
	rm -rf dist/

test: pyc
	$(TESTRUNNER)

pyc:
	find . -name "*.pyc" -exec rm {} \;

watch:
	tdaemon . $(TESTRUNNER) --custom-args="$(WATCHTESTFLAGS)"

release: bump merge publish develop tag

bump:
	$(EDITOR) HISTORY.rst turses/__init__.py Makefile 
	git add -u
	git commit

merge:
	git stash
	git checkout master
	git merge develop

develop:
	git checkout develop

publish:
	$(PY) setup.py sdist upload

tag:
	@echo "===================="
	@echo "Tag the release NOW!"
	@echo "===================="

stats:
	@echo "pep8"
	@echo "===="
	@echo
	@echo "Warnings: " `pep8 . | grep -o "W[0-9]*.*"  | wc -l`
	@echo "Errors: " `pep8 . | grep -o "E[0-9]*.*"  | wc -l`
	@echo
	@echo "pyflakes"
	@echo "========"
	@echo 
	@echo "Errors: `pyflakes . | wc -l`"
