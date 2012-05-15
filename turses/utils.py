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
from threading import Thread
from calendar import timegm
import re
from re import sub, findall
from subprocess import call
from sys import stdout
from os import devnull
from gettext import gettext as _
from functools import wraps, partial

from turses import version as turses_version

URL_REGEX = re.compile('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
                       '(?:%[0-9a-fA-F][0-9a-fA-F]))+')


def parse_arguments():
    """Parse arguments from the command line."""

    parser_title = "turses: Twitter client featuring a sexy curses interface."
    parser = ArgumentParser(parser_title)

    parser.add_argument("-a", "--account",
            help=_("Use account with the specified username."))

    parser.add_argument("-c", "--config",
            help=_("Use the specified configuration file."))

    help = _("Generate a default configuration file is the specified path.")
    parser.add_argument("-g", "--generate-config",
                        help=help)

    version = "turses %s" % turses_version
    parser.add_argument("-v", "--version", action="version", version=version,
            help=_("Show the current version of turses"))

    args = parser.parse_args()
    return args


def wrap_exceptions(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments.

    Executes the decorated function in a try except block and calls
    `on_success` (if given) if no exception was raised, otherwise calls
    `on_error` (if given).
    """
    @wraps(func)
    def wrapper(self=None, *args, **kwargs):
        on_error = kwargs.pop('on_error', None)
        on_success = kwargs.pop('on_success', None)

        try:
            result = func(self, *args, **kwargs)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()
            return result

    return wrapper


def async(func):
    """
    Decorator for executing a function asynchronously.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper


def html_unescape(string):
    """Unescape HTML entities from `string`."""
    def entity_replacer(m):
        entity = m.group(1)
        if entity in entitydefs:
            return entitydefs[entity]
        else:
            return m.group(0)

    return sub(r'&([^;]+);', entity_replacer, string)


def matches_word(regex, word):
    """
    Return `True` if the whole `word` is matched by `regex`, `False`
    otherwise.
    """
    match = regex.match(word)
    if match:
        return match.start() == 0 and match.end() == len(word)
    return False

is_url = partial(matches_word, URL_REGEX)


def get_urls(text):
    return findall(URL_REGEX, text)


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
