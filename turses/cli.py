# -*- coding: utf-8 -*-

"""
turses.cli
~~~~~~~~~~

Handle the invocation of `turses` from the command line.
"""

from sys import stdout
from argparse import ArgumentParser
from os import getenv
from gettext import gettext as _

from urwid import set_encoding

from turses import __name__
from turses import version as turses_version
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


def parse_arguments():
    """Parse arguments from the command line."""

    parser_title = "turses: Twitter client featuring a sexy curses interface."
    parser = ArgumentParser(parser_title)

    # load account
    parser.add_argument("-a", 
                        "--account",
                        help=_("Use account with the specified username."))

    # load non-default configuration
    parser.add_argument("-c", 
                        "--config",
                        help=_("Use the specified configuration file."))

    # generate configuration
    generate_config_help = _("Generate a default configuration file is "
                             "the specified path.")
    parser.add_argument("-g", 
                        "--generate-config",
                        help=generate_config_help)

    # version
    version = "turses %s" % turses_version
    parser.add_argument("-v", 
                        "--version", 
                        action="version", 
                        version=version,
                        help=_("Show the current version of turses"))

    # debug mode
    parser.add_argument("-d", 
                        "--debug",
                        help=_("Start turses in debug mode."))


    args = parser.parse_args()
    return args


def main():
    set_title(__name__)
    set_encoding('utf8')

    args = parse_arguments()

    # stdout
    if any([getattr(args, 'help', False), 
            getattr(args, 'version', False),
            getattr(args, 'debug', False)]):
        # we are going to print information to stdout
        save_and_restore_stdout = False
    else:
        save_and_restore_stdout = True

    if save_and_restore_stdout:
        save_stdout()

    # configuration
    configuration = Configuration(args)
    configuration.load()

    # view
    curses_interface = CursesInterface(configuration)

    # controller
    turses = Turses(configuration=configuration,
                    ui=curses_interface,
                    api_backend=TweepyApi)
    try:
        turses.start()
    except KeyboardInterrupt:
        pass
    finally:
        if save_and_restore_stdout:
            restore_stdout()

        restore_title()

        exit(0)
