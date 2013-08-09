# -*- coding: utf-8 -*-

"""
Handle the invocation of ``turses`` from the command line.
"""

import logging
from sys import stdout
from argparse import ArgumentParser
from os import getenv
from gettext import gettext as _

from urwid import set_encoding

from turses import __name__
from turses import version as turses_version
from turses.config import configuration, LOG_FILE
from turses.models import TimelineList
from turses.ui import CursesInterface
from turses.api.base import AsyncApi
from turses.api.debug import MockApi
from turses.api.backends import TweepyApi
from turses.core import Controller as Turses


def save_stdout():
    """Save shell screen."""
    stdout.write("\033[?1049h\033[H")


def restore_stdout():
    """Restore saved shell screen."""
    stdout.write("\033[?1049l")


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
    """Restore original window title."""
    if getenv('TMUX'):
        set_title(getenv('SHELL').split('/')[-1])


def create_async_api(api_backend_cls):
    """
    Create an asynchronous API given a concrete API class ``api_backend_cls``.
    """
    oauth_token = configuration.oauth_token
    oauth_token_secret = configuration.oauth_token_secret

    return AsyncApi(api_backend_cls,
                    access_token_key=oauth_token,
                    access_token_secret=oauth_token_secret,)


def read_arguments():
    """Read arguments from the command line."""

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

    # load session
    parser.add_argument("-s",
                        "--session",
                        help=_("Load the specified session"))

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
                        action="store_true",
                        help=_("Start turses in debug mode."))

    # offline debug mode
    parser.add_argument("-o",
                        "--offline",
                        action="store_true",
                        help=_("Start turses in offline debug mode."))

    args = parser.parse_args()
    return args


def main():
    """
    Launch ``turses``.
    """
    set_title(__name__)
    set_encoding('utf8')

    args = read_arguments()

    # check if stdout has to be restored after program exit
    if any([args.debug,
            args.offline,
            getattr(args, 'help', False),
            getattr(args, 'version', False)]):
        # we are going to print information to stdout
        save_and_restore_stdout = False
    else:
        save_and_restore_stdout = True

    if save_and_restore_stdout:
        save_stdout()

    # parse arguments and load configuration
    configuration.parse_args(args)
    configuration.load()

    # start logger
    logging.basicConfig(filename=LOG_FILE,
                        level=configuration.logging_level)

    # create view
    curses_interface = CursesInterface()

    # create model
    timeline_list = TimelineList()

    # create API
    api = create_async_api(MockApi if args.offline else TweepyApi)

    # create controller
    turses = Turses(ui=curses_interface,
                    api=api,
                    timelines=timeline_list,)

    try:
        turses.start()
    except:
        # A unexpected exception occurred, open the debugger in debug mode
        if args.debug or args.offline:
            import pdb
            pdb.post_mortem()
    finally:
        if save_and_restore_stdout:
            restore_stdout()

        restore_title()

        exit(0)
