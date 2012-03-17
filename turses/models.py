###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import re


retweet_re = re.compile('^RT @\w+:')

def is_tweet(status):
    return status.__class__ == Status

def is_retweet(status):
    return bool(retweet_re.match(status.text))

def is_DM(status):
    return status.__class__ == DirectMessage

def get_authors_username(status):
    """Returns the original author's username of the given status."""
    username = status.sender_screen_name
    return ''.join(['@', username])

def is_username(string):
    return string.startswith('@')

def sanitize_username(username):
    is_legal_username_char = lambda char: char.isalnum()
    sanitized = filter(is_legal_username_char, username[1:])
    return ''.join(['@', sanitized])

def get_mentioned_usernames(status):
    usernames = filter(is_username, status.text.split())
    return map(sanitize_username, usernames)

def is_valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= 140

def is_valid_search_text(text):
    """Checks the validity of a search text."""
    return bool(text)

def is_valid_username(username):
    return username.isalnum()

# TODO
class Status(object):

    def __init__(self,
                 sender_screen_name=''):
        pass


class DirectMessage(object):
    pass
