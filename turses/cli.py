# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

This module contains the logic to launch `turses` with a curses interface.
"""

from .util import parse_arguments
from .config import Configuration
from .controller import CursesController
from .constant import palette
from .ui.curses import CursesInterface


def main():
    try:
        configuration = Configuration(parse_arguments())
        ui = CursesInterface()
        CursesController(palette, 
                         configuration, 
                         ui)
    except KeyboardInterrupt:
        exit(0)
