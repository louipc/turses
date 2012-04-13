# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

This module contains the logic to launch `turses` with a curses interface.
"""

from .utils import parse_arguments
from .config import TursesConfiguration
from .controller import CursesController
from .defaults import palette
from .ui.curses import CursesInterface
from .api.backends import TweepyApi


def main():
    try:
        args = parse_arguments()

        configuration = TursesConfiguration(args)
        ui = CursesInterface(configuration)

        # start `turses`
        CursesController(palette=palette, 
                         configuration=configuration, 
                         ui=ui,
                         api_backend=TweepyApi)
    except KeyboardInterrupt:
        exit(0)
