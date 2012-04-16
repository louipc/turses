# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

This module contains the logic to launch `turses` with a curses interface.
"""

from urwid import set_encoding

from .utils import parse_arguments
from .config import Configuration
from .controller import CursesController
from .ui import CursesInterface
from .api.backends import TweepyApi


def main():
    try:
        set_encoding('utf8')

        args = parse_arguments()
        configuration = Configuration(args)
        configuration.load()
        ui = CursesInterface(configuration)

        # start `turses`
        CursesController(configuration=configuration, 
                         ui=ui,
                         api_backend=TweepyApi)
    except KeyboardInterrupt:
        exit(0)
