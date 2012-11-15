APPNAME=turses

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

release: bump merge tag push publish

bump:
	$(EDITOR) HISTORY.rst turses/__init__.py
	git add -u
	git commit -m "bump `cat turses/__init__.py | grep -o "., ., ." | tr -s ', ' '.'`"

merge:
	git stash
	git checkout master
	git merge develop

tag:
	git tag v`cat turses/__init__.py | grep -o "., ., ." | tr -s ', ' '.'`

push:
	git push --tags origin master

publish:
	$(PY) setup.py sdist upload
