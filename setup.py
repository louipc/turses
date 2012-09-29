# -*- coding: utf-8 -*-

"""
turses
======

A Twitter client for the console.

The goal of the project is to build a full-featured, lightweight, and extremely 
configurable Twitter client.

Documentation
-------------

The documentation for ``turses`` is `available on ReadTheDocs
<http://turses.readthedocs.org>`_.

License
-------

``turses`` is licensed under a GPLv3 license, see ``LICENSE`` for details.

Authors
-------

``turses`` is based on `Tyrs`_ by `Nicolas Paris`_.

.. _`Tyrs`: http://tyrs.nicosphere.net
.. _`Nicolas Paris`: http://github.com/Nic0

See ``AUTHORS`` for a full list of contributors.
"""

from setuptools import setup, find_packages
from sys import version_info

import turses

NAME = "turses"

REQUIREMENTS = [
    "oauth2",
    "urwid",
    "tweepy",
]
if version_info[:2] == (2, 6):
    REQUIREMENTS.append("argparse")

TEST_REQUIREMENTS = list(REQUIREMENTS)
TEST_REQUIREMENTS.extend(["mock", "nose", "coverage", "tox"])

try:
    long_description = open("README.rst").read() + "\n\n" + open("HISTORY.rst").read()
except IOError:
    long_description = __doc__


setup(name=NAME,
      version=turses.version,
      author="Alejandro Gómez",
      author_email="alejandroogomez@gmail.com",
      url="http://github.com/alejandrogomez/turses",
      description="A Twitter client for the console.",
      long_description=long_description,
      keywords="twitter client, curses, console, twitter",
      packages=find_packages(),
      entry_points={
          'console_scripts':
            ['turses = turses.cli:main']
      },
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console :: Curses",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Operating System :: MacOS",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications",
      ],
      install_requires=REQUIREMENTS,
      tests_require=TEST_REQUIREMENTS)
