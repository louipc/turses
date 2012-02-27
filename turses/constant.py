###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

# palette for the ncurses interface created with `urwid`
palette = [
    ['body','default', '', 'standout'],
    ['focus','dark red', '', 'standout'],
    ['header','light blue', ''],
    ['line', 'dark blue', ''],
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
    # TODO
    'identica': {
        'consumer_key':     '',
        'consumer_secret':  ''
    }
}

key = {
    'up':                'k',
    'down':              'j',
    'left':              'J',
    'right':             'K',
    'quit':              'q',
    'tweet':             't',
    'clear':             'c',
    'retweet':           'r',
    'retweet_and_edit':  'R',
    'delete':            'C',
    'update':            'u',
    'follow_selected':   'f',
    'unfollow_selected': 'l',
    'follow':            'F',
    'unfollow':          'L',
    'openurl':           'o',
    'open_image':        'ctrl i',
    'home':              'h',
    'mentions':          'm',
    'reply':             'M',
    'back_on_top':       'g',
    'back_on_bottom':    'G',
    'getDM':             'd',
    'sendDM':            'D',
    'search':            's',
    'search_user':       'U',
    'search_current_user': 'ctrl f',
    'search_myself':     'ctrl u',
    'redraw':            'ctrl l',
    'fav':               'b',
    'get_fav':           'B',
    'delete_fav':        'ctrl b',
    'thread':            'T',
    'waterline':         'w',
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

