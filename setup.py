# -*- coding: utf-8 -*-

"""
turses installation.
"""

from setuptools import setup, find_packages

import turses

NAME = "turses"

REQUIREMENTS = [
    "oauth2",
    "urwid",
    "tweepy",
]
TEST_REQUIREMENTS = list(REQUIREMENTS)
TEST_REQUIREMENTS.extend(["mock", "nose", "coverage"])

try:
    long_description = open("README.rst").read() + "\n\n" + open("HISTORY.rst").read()
except IOError:
    long_description = ""


setup(name=NAME,
      version=turses.version,
      author="Alejandro Gómez",
      author_email="alejandroogomez@gmail.com",
      url="http://github.com/alejandrogomez/turses",
      description="A Twitter client with a curses interface.",
      long_description=long_description,
      keywords="twitter client, curses, console",
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
          "Programming Language :: Python :: 2.7",
          "Topic :: Communications",
      ],
      install_requires=REQUIREMENTS,
      tests_require=TEST_REQUIREMENTS)
