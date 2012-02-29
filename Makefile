APPNAME=turses
VERSION=0.0.2
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=nosetests
TESTFLAGS=--with-coverage --cover-package=turses

all: turses

turses: clean test dist install

dist:  
	$(DIST)

install: $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean:
	rm -rf dist/

test:
	$(TESTRUNNER) $(TESTFLAGS)

release: clean test upload
	
upload:
	$(PY) setup.py sdist upload
