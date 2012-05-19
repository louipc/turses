# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

Handle the invocation of `turses` from the command line.
"""

from sys import stdout
from os import getenv

from urwid import set_encoding

from turses import __name__
from turses.utils import parse_arguments
from turses.config import Configuration
from turses.ui import CursesInterface
from turses.api.backends import TweepyApi
from turses.core import Turses


def set_title(string):
    try:
        if getenv('TERM').startswith("screen"):
            if getenv('TMUX'):
                stdout.write("\033k%s\033\\" % string)  # for tmux
            else:
                stdout.write("\033_%s\033\\" % string)  # for GNU screen
        else:
            stdout.write("\x1b]2;%s\x07" % string)
    except:
        pass


def main():
    try:
        set_title(__name__)
        set_encoding('utf8')

        # save current shell screen
        print "\033[?1049h\033[H"

        args = parse_arguments()

        configuration = Configuration(args)
        configuration.load()
        ui = CursesInterface(configuration)

        # start `turses`
        Turses(configuration=configuration,
            ui=ui,
            api_backend=TweepyApi)
    except KeyboardInterrupt:
        pass
    finally:
        # restore original window title
        if getenv('TMUX'):
            set_title(getenv('SHELL').split('/')[-1])
        # restore original shell screen
        print "\033[?1049l"
        exit(0)
