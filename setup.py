# -*- coding: utf-8 -*-

import os
import sys
from distutils.core import setup

import turses


name = "turses"

requirements = [
    "oauth2",
    "urwid",
    "tweepy",
]
test_requirements = list(requirements)
test_requirements.extend(["mock", "nose", "coverage"])

try:
    long_description = open("README.rst").read() + "\n\n" + open("HISTORY.rst").read()
except IOError:
    long_description = ""

# Publish Helper.
if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(name="turses",
      version=turses.version,
      author="Alejandro Gómez",
      author_email="alejandroogomez@gmail.com",
      url="http://github.com/alejandrogomez/turses",
      description="A Twitter client with a curses interface.",
      long_description=long_description,
      keywords="twitter client curses",
      packages=[
          "turses",
          "turses.api",
      ],
      package_data={'': ['LICENSE']},
      include_package_data=True,
      package_dir={
          "turses":  "turses"
      },
      scripts=['bin/turses'],
      platforms=["linux"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console :: Curses",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications"
      ],
      install_requires=requirements,
      tests_require=test_requirements,)
