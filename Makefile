APPNAME=turses
VERSION=v0.1alpha
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTS=$(shell find -name "test_*.py")

all: turses

turses: dist install

dist:  
	$(DIST)

install: $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean:
	rm -rf dist/
