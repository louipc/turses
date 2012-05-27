# -*- coding: utf-8 -*-

"""
This module contains functions used across different modules.
"""

from re import findall
from re import compile as compile_regex
from subprocess import call
from sys import stdout
from os import devnull
from functools import partial


URL_REGEX = compile_regex('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
                          '(?:%[0-9a-fA-F][0-9a-fA-F]))+')


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


def spawn_process(command, args):
    """
    Spawn the process `command` with `args` as arguments in the background.
    """
    with open(devnull, 'w') as null:
        call(' '.join([command, args, '&']),
             shell=True,
             stdout=null,
             stderr=null,)
