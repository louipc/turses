APPNAME=turses
VERSION=0.1.10
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=nosetests
TESTFLAGS=--nocapture --logging-clear-handlers --with-coverage --cover-package=turses
WATCHTESTFLAGS=--verbosity=0


all: turses

turses: clean test dist install

dist: clean
	$(DIST)

install: dist $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean: pyc
	rm -rf dist/

test: pyc
	$(TESTRUNNER) $(TESTFLAGS)

pyc:
	find . -name "*.pyc" -exec rm {} \;

watch:
	tdaemon . $(TESTRUNNER) --custom-args="$(WATCHTESTFLAGS)"

bump:
	$(EDITOR) HISTORY.rst turses/__init__.py Makefile 
