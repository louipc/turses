# -*- coding: utf-8 -*-

"""
turses.utils
~~~~~~~~~~~~

This module contains functions used across different modules.
"""

from argparse import ArgumentParser
from htmlentitydefs import entitydefs
from time import strftime, gmtime
from calendar import timegm
from re import sub, findall
from subprocess import call
from sys import stdout
from os import devnull

from . import __version__

def parse_arguments():
    """Parse all arguments from the command line."""

    parser = ArgumentParser("turses: Twitter client with a sexy curses interface.")

    parser.add_argument("-a", "--account",
            help="Use another account, store in a different file.")

    parser.add_argument("-c", "--config",
            help="Use another configuration file.")

    parser.add_argument("-g", "--generate-config",
            help="Generate a default configuration file.")

    version = "turses %s" % __version__
    parser.add_argument("-v", "--version", action="version", version=version,
            help="Show the current version of turses")

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
    return findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def encode(string):
    try:
        return string.encode(stdout.encoding, 'replace')
    except AttributeError:
        return string

def timestamp_from_datetime(datetime):
    return timegm(datetime.utctimetuple())

def spawn_process(command, args):
    """
    Spawn the process `command` with `args` as arguments in the background.
    """
    with open(devnull, 'w') as null:
        call(' '.join([command, args, '&']),
             shell=True,
             stdout=null,
             stderr=null,)
