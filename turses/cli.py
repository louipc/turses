###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import argparse

from config import Configuration
from turses import Turses

__version__ = '0.1alpha'


def arguments():
    """Parse all arguments from the command line."""

    parser = argparse.ArgumentParser(
            "turses: a ncurses Twitter client written in Python.")

    parser.add_argument("-a", "--account",
            help="Use another account, store in a different file.")

    parser.add_argument("-c", "--config",
            help="Use another configuration file.")

    parser.add_argument("-g", "--generate-config",
            help="Generate a default configuration file.")

    version = "turses %s" % __version__
    parser.add_argument("-v", "--version", action="version", version=version,
            help="Show the current version of turses")

    args = parser.parse_args()
    return args


def main():
    configuration = Configuration(arguments())
    Turses(configuration)
