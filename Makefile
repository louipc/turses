APPNAME=turses
VERSION=0.0.1
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTS=$(shell find -name "test_*.py")

all: turses

turses: clean dist install

dist:  
	$(DIST)

install: $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean:
	rm -rf dist/
