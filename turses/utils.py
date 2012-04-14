# -*- coding: utf-8 -*-

"""
turses.utils
~~~~~~~~~~~~

This module contains functions used across different modules.
"""

from argparse import ArgumentParser
from datetime import datetime, timedelta
from email.utils import parsedate_tz
from htmlentitydefs import entitydefs
from time import strftime, gmtime
from calendar import timegm
from re import sub, findall
from subprocess import call
from sys import stdout
from os import devnull
from gettext import gettext as _

from . import version as turses_version

def parse_arguments():
    """Parse arguments from the command line."""

    parser = ArgumentParser("turses: Twitter client featuring a sexy curses interface.")

    parser.add_argument("-a", "--account",
            help=_("Use account with the specified username."))

    parser.add_argument("-c", "--config",
            help=_("Use the specified configuration file."))

    parser.add_argument("-g", "--generate-config",
            help=_("Generate a default configuration file is the specified path."))

    version = "turses %s" % turses_version
    parser.add_argument("-v", "--version", action="version", version=version,
            help=_("Show the current version of turses"))

    args = parser.parse_args()
    return args

def get_time():
    return strftime('%H:%M:%S', gmtime())

def html_unescape(str):
    """Unescapes HTML entities."""
    def entity_replacer(m):
        entity = m.group(1)
        if entity in entitydefs:
            return entitydefs[entity]
        else:
            return m.group(0)

    return sub(r'&([^;]+);', entity_replacer, str)

def get_urls(text):
    # TODO: improve this
    return findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def encode(string):
    try:
        return string.encode(stdout.encoding, 'replace')
    except AttributeError:
        return string

def timestamp_from_datetime(datetime):
    return timegm(datetime.utctimetuple())

def datetime_from_twitter_datestring(datestring):
    """
    Return a datetime object that corresponds to the given `datestring`.

    Twitter API returns date strings with the format: %a %b %d %H:%M:%S %z %Y
    """
    # this code is borrowed from a StackOverflow answer: 
    #   http://stackoverflow.com/a/7704266
    time_tuple = parsedate_tz(datestring.strip())
    dt = datetime(*time_tuple[:6])
    return dt - timedelta(seconds=time_tuple[-1])

def spawn_process(command, args):
    """
    Spawn the process `command` with `args` as arguments in the background.
    """
    with open(devnull, 'w') as null:
        call(' '.join([command, args, '&']),
             shell=True,
             stdout=null,
             stderr=null,)
