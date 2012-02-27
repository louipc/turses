###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
import re
import string
from htmlentitydefs import entitydefs
from time import strftime, gmtime

retweet_re = re.compile('^RT @\w+:')

def get_time():
    return strftime('%H:%M:%S', gmtime())

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

def is_retweet(status):
    return bool(retweet_re.match(status.text))
