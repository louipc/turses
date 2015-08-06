APPNAME=turses

PY=python
DIST=$(PY) setup.py sdist
PIPI=pip install
PIPFLAGS=--ignore-installed --no-deps

TESTRUNNER=py.test
COVERTESTFLAGS=--with-coverage --cover-package=turses --cover-html
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

coverage: pyc
	$(TESTRUNNER) $(COVERTESTFLAGS)

pyc:
	find . -name "*.pyc" -exec rm {} \;

release: bump publish tag push

bump:
	$(EDITOR) HISTORY.rst turses/__init__.py
	git add -u
	git commit -m "bump `cat turses/__init__.py | grep -o "[[:digit:]]*, [[:digit:]]*, [[:digit:]]*" | tr -s ', ' '.'`"

tag:
	git tag v`cat turses/__init__.py | grep -o "[[:digit:]]*, [[:digit:]]*, [[:digit:]]*" | tr -s ', ' '.'`

push:
	git push --tags origin master

publish:
	$(PY) setup.py sdist upload

watch:
	watchmedo shell-command --patterns="*.py" --recursive --command="$(TESTRUNNER) $(WATCHTESTFLAGS)"
