###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from distutils.core import setup

name = "turses"
version = "0.0.4"

requirements = open("pip-requirements.txt").readlines()
tests_requirements = open("dev-requirements.txt").readlines()

long_description = open("README.rst").read() ++ "\n\n" + open("HISTORY.rs").read() 

setup(name="turses",
      version=version,
      author="Alejandro Gómez",
      author_email="alejandroogomez@gmail.com",
      license="GPLv3",
      description="A Twitter client with a curses interface.",
      long_description=long_description,
      keywords="twitter client curses",
      packages=[
          "turses", 
          "turses.ui"
      ],
      package_dir={
          "turses":  "turses"
      },
      scripts=["bin/turses"],
      platforms=["linux"],
      classifiers=[
          "Development Status :: 4 - Beta",
          "Environment :: Console :: Curses",
          "Intended Audience :: End Users/Desktop",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Natural Language :: English",
          "Operating System :: POSIX :: Linux",
          "Programming Language :: Python :: 2",
      ],
      install_requires=requirements,
      tests_require=tests_requirements,)
