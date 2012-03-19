###############################################################################
#                               coding=utf-8                                  #
#            Copyright (c) 2012 turses contributors. See AUTHORS.             #
#         Licensed under the GPL License. See LICENSE for full details.       #
###############################################################################

from .util import parse_arguments
from .config import Configuration
from .controller import Turses
from .ui.curses import CursesInterface


def main():
    try:
        configuration = Configuration(parse_arguments())
        ui = CursesInterface()
        Turses(configuration, ui)
    except KeyboardInterrupt:
        exit(0)
