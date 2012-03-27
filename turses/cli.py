# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

This module contains the logic to launch `turses` with a curses interface.
"""

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
