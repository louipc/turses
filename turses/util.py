###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import argparse
import re
import sys
import string
from htmlentitydefs import entitydefs
from time import strftime, gmtime

# TODO this shouldn't be `python-twitter` specific
from twitter import Status, DirectMessage

from . import __version__

retweet_re = re.compile('^RT @\w+:')
username_re = re.compile('@\w+')

def parse_arguments():
    """Parse all arguments from the command line."""

    parser = argparse.ArgumentParser(
            "turses: a ncurses Twitter client written in Python.")

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

def get_usernames(text):
    """Retrieve all the Twitter usernames found on `text`."""
    # TODO
    pass

def cut_attag(name):
    if name[0] == '@':
        name = name[1:]
    return name

def get_exact_nick(word):
    if word[0] == '@':
        word = word[1:]
    alphanum = string.letters + string.digits
    try:
        while word[-1] not in alphanum:
            word = word[:-1]
    except IndexError:
        pass
    return word

def html_unescape(str):
    """Unescapes HTML entities."""
    def entity_replacer(m):
        entity = m.group(1)
        if entity in entitydefs:
            return entitydefs[entity]
        else:
            return m.group(0)

    return re.sub(r'&([^;]+);', entity_replacer, str)

def get_urls(text):
    return re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)

def encode(string):
    try:
        return string.encode(sys.stdout.encoding, 'replace')
    except AttributeError:
        return string

def valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= 140

def valid_search_text(text):
    """Checks the validity of a search text."""
    return bool(text)

def is_valid_username(username):
    return username.isalnum()

# TODO: make this functions library independent
def is_tweet(status):
    return status.__class__ == Status

def is_retweet(status):
    return bool(retweet_re.match(status.text))

def is_DM(status):
    return status.__class__ == DirectMessage

def get_authors_username(status):
    """Returns the original author's username of the given status."""
    if is_tweet(status) or is_retweet(status):
        username = status.user.screen_name
    elif is_DM(status):
        username = status.sender_screen_name
    return ''.join(['@', username])
    def is_username(string):
        return string.startswith('@')

def is_username(string):
    return string.startswith('@')

def sanitize_username(username):
    is_legal_username_char = lambda char: char.isalnum()
    sanitized = filter(is_legal_username_char, username[1:])
    return ''.join(['@', sanitized])

def get_mentioned_usernames(status):
    usernames = filter(is_username, status.text.split())
    return map(sanitize_username, usernames)
