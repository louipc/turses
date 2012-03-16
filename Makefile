APPNAME=turses
VERSION=0.0.4
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=nosetests
TESTFLAGS=--with-coverage --cover-package=turses

all: turses

turses: clean test dist install

dist: pyc 
	$(DIST)

install: $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean: pyc
	rm -rf dist/

test:
	$(TESTRUNNER) $(TESTFLAGS)

pyc:
	find . -name "*.pyc" -exec rm {} \;

release: clean test upload
	
upload:
	$(PY) setup.py sdist upload
