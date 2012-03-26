APPNAME=turses
VERSION=0.0.9
DISTPKG=dist/$(APPNAME)-$(VERSION).tar.gz

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=nosetests
TESTFLAGS=--with-progressive --logging-clear-handlers --with-coverage --cover-package=turses
WATCHTESTFLAGS=--verbosity=0


all: turses

turses: clean test dist install

dist: clean
	$(DIST)

install: dist $(DISTPKG)
	$(PIPI) $(PIPFLAGS) $(DISTPKG)

clean: pyc
	rm ~/.config/turses/turses.cfg
	rm -rf dist/

test: pyc
	$(TESTRUNNER) $(TESTFLAGS)

pyc:
	find . -name "*.pyc" -exec rm {} \;

release: clean test master upload

master:
	git stash
	git checkout master
	
upload:
	$(PY) setup.py sdist upload

watch:
	tdaemon . $(TESTRUNNER) --custom-args="$(WATCHTESTFLAGS)"
