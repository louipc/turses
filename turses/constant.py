###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from turses import __version__


# palette for the curses interface created with `urwid`
palette = [
    ['body', 'default', '', 'standout'],
    ['focus','dark red', '', 'standout'],
    ['header', 'light blue', ''],
    ['line', 'dark blue', ''],
    ['favorited', 'yellow', ''],
    ['info_msg', 'dark green', ''],
    ['warn_msg', 'dark red', ''],
    ['active_tab', 'light blue', ''],
    ['inactive_tab', 'dark blue', ''],
    ['read', 'dark blue', ''],
    ['unread', 'dark red', ''],
    ['hashtag', 'dark green', ''],
    ['attag', 'brown', ''],
    ['highlight', 'dark red', ''],
    ['highlight_nick', 'light red', ''],
    ['help_bar', 'yellow', 'dark blue'],
    ['help_key', 'dark red', ''],
]

token = {
    'twitter': {
        'consumer_key':     'OEn4hrNGknVz9ozQytoR0A',
        'consumer_secret':  'viud49uVgdVO9dnOGxSQJRo7jphTioIlEn3OdpkZI'
    },
    'identica': {
        'consumer_key':     '29d5dec21c629682e10bc45f11baf3ab',
        'consumer_secret':  '0f25e5b8e441492bdc654583e21451d4'
    }
}

key = {
    # Motion
    'up':                     'k',
    'down':                   'j',
    'left':                   'h',
    'right':                  'l',
    'scroll_to_top':          'g',
    'scroll_to_bottom':       'G',
    # Buffers
    'shift_buffer_left':      '<',
    'shift_buffer_right':     '>',
    'shift_buffer_beggining': 'ctrl a',
    'shift_buffer_end':       'ctrl e',
    'activate_first_buffer':  'a',
    'activate_last_buffer':   'e',
    'delete_buffer':          'd',
    'clear':                  'c',
    # Tweets
    'tweet':                  't',
    'delete_tweet':           'X',
    'reply':                  'r',
    'retweet':                'R',
    'retweet_and_edit':       'E',
    'sendDM':                 'D',
    'update':                 'u',
    # Friendship
    'follow_selected':        'f',
    'unfollow_selected':      'U',
    # Favorites
    'fav':                    'b',
    'delete_fav':             'ctrl b',
    # Timelines
    'home':                   '.',
    'favorites':              'B',
    'mentions':               'm',
    'DMs':                    'M',
    'search':                 '/',
    'search_user':            '@',
    'search_myself':          'ctrl u',
    'search_current_user':    'ctrl f',
    'thread':                 'T',
    'user_info':              'i',
    'help':                   '?',
    # Misc
    'quit':                   'q',
    'openurl':                'o',
    'open_image':             'ctrl i',
    'redraw':                 'ctrl l',
}

params = {
    'refresh':              2,
    'tweet_border':         1,
    'relative_time':        1,
    'retweet_by':           1,
    'margin':               1,
    'padding':              2,
    'openurl_command':      'firefox %s',
    'open_image_command':   'feh %s',
    'transparency':         True,
    'activities':           True,
    'compact':              False,
    'help':                 True,
    'old_skool_border':     False,
    'box_position':         1,
    'url_shorter':          'ur1ca',
    'logging_level':        3,
    'header_template':      ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'proxy':                None,
    'beep':                 False,
}

filter = {
    'activate':         False,
    'myself':           False,
    'behavior':         'all',
    'except':           [],
}

banner = [ 
     "   _                             ",
     " _| |_ _   _ _ __ ___  ___  ____ ",
     "|_   _| | | | '__/ __|/   \/ ___|",
     "  | | | | | | |  |   \  _ ||   \\ ",
     "  | |_| |_| | |  \__ |  __/\__ | ",
     "  \___|\____|_| |____/\___||___/ ",
     "  ······························ ",
     "%s" % __version__,
]
