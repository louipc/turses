# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

Handle the invocation of `turses` from the command line.
"""

from sys import stdout

from urwid import set_encoding

from turses import __name__
from turses.utils import parse_arguments
from turses.config import Configuration
from turses.ui import CursesInterface
from turses.api.backends import TweepyApi
from turses.core import Turses


def set_title(string):
    try:
        stdout.write("\x1b]2;%s\x07" % string)
    except:
        pass

def main():
    try:
        set_title(__name__)
        set_encoding('utf8')

        args = parse_arguments()

        configuration = Configuration(args)
        configuration.load()
        ui = CursesInterface(configuration)

        # start `turses`
        Turses(configuration=configuration,
            ui=ui,
            api_backend=TweepyApi)
    except KeyboardInterrupt:
        exit(0)
