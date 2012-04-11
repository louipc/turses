# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

This module contains the logic to launch `turses` with a curses interface.
"""

from .utils import parse_arguments
from .config import Configuration
from .controller import CursesController
from .constant import palette
from .ui.curses import CursesInterface
from .api.backends import TweepyApi


def main():
    try:
        args = parse_arguments()
        configuration = Configuration(args)
        ui = CursesInterface(configuration)

        # start `turses`
        CursesController(palette=palette, 
                         configuration=configuration, 
                         ui=ui,
                         api_backend=TweepyApi)
    except KeyboardInterrupt:
        exit(0)
