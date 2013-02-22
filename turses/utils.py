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

# username
username_regex = compile_regex(r'[A-Za-z0-9_]+')
is_username = partial(matches_word, username_regex)
sanitize_username = partial(filter, is_username)
prepend_at = lambda username: '@%s' % username

# hashtag
hashtag_regex = compile_regex(r'#.+')
is_hashtag = partial(matches_word, hashtag_regex)

# URL
is_url = partial(matches_word, URL_REGEX)


def get_urls(text):
    return findall(URL_REGEX, text)


def encode(string):
    try:
        return string.encode(stdout.encoding, 'replace')
    except (AttributeError, TypeError):
        return string

# For Python < 2.7
# Code borrowed from python 2.7.3 stdlib
def total_ordering(cls):
    """Class decorator that fills in missing ordering methods"""
    convert = {
        '__lt__': [('__gt__', lambda self, other: not (self < other or self == other)),
                   ('__le__', lambda self, other: self < other or self == other),
                   ('__ge__', lambda self, other: not self < other)],
        '__le__': [('__ge__', lambda self, other: not self <= other or self == other),
                   ('__lt__', lambda self, other: self <= other and not self == other),
                   ('__gt__', lambda self, other: not self <= other)],
        '__gt__': [('__lt__', lambda self, other: not (self > other or self == other)),
                   ('__ge__', lambda self, other: self > other or self == other),
                   ('__le__', lambda self, other: not self > other)],
        '__ge__': [('__le__', lambda self, other: (not self >= other) or self == other),
                   ('__gt__', lambda self, other: self >= other and not self == other),
                   ('__lt__', lambda self, other: not self >= other)]
    }
    roots = set(dir(cls)) & set(convert)
    if not roots:
        raise ValueError('must define at least one ordering operation: < > <= >=')
    root = max(roots) # prefer __lt__ to __le__ to __gt__ to __ge__
    for opname, opfunc in convert[root]:
        if opname not in roots:
            opfunc.__name__ = opname
            opfunc.__doc__ = getattr(int, opname).__doc__
            setattr(cls, opname, opfunc)
    return cls
