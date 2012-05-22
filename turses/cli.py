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


def save_stdout():
    """Save shell screen."""
    print "\033[?1049h\033[H"


def restore_stdout():
    """Restore saved shell screen."""
    print "\033[?1049l"


def set_title(string):
    """Set window title."""
    try:
        if getenv('TERM').startswith("screen"):
            # terminal multiplexors
            if getenv('TMUX'):
                stdout.write("\033k%s\033\\" % string)  # for tmux
            else:
                stdout.write("\033_%s\033\\" % string)  # for GNU screen
        else:
            # terminal
            stdout.write("\x1b]2;%s\x07" % string)
    except:
        pass


def restore_title():
    # restore original window title
    if getenv('TMUX'):
        set_title(getenv('SHELL').split('/')[-1])


def main():
    try:
        set_title(__name__)
        set_encoding('utf8')

        save_stdout()

        args = parse_arguments()

        configuration = Configuration(args)
        configuration.load()

        curses_interface = CursesInterface(configuration)

        turses = Turses(configuration=configuration,
                        ui=curses_interface,
                        api_backend=TweepyApi)
        turses.start()
    except KeyboardInterrupt:
        pass
    finally:
        restore_stdout()
        restore_title()

        exit(0)
