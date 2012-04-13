# -*- coding: utf-8 -*-

"""
turses.defaults
~~~~~~~~~~~~~~~

This module contains the programs defaults.
"""

palette = [
    # Tabs
    ['active_tab',  'white', ''],
    ['visible_tab', 'light cyan', ''],
    ['inactive_tab', 'dark blue', ''],

    # Statuses
    ['header', 'light blue', ''],
    ['body', 'default', '', 'standout'],
    ['focus','dark red', '', 'standout'],
    ['line', 'dark blue', ''],
    ['unread', 'dark red', ''],
    ['read', 'dark blue', ''],
    ['favorited', 'yellow', ''],

    # Text
    ['highlight', 'dark red', ''],
    ['highlight_nick', 'light red', ''],
    ['attag', 'brown', ''],
    ['hashtag', 'dark green', ''],

    # Messages
    ['error', 'white', 'dark red'],
    ['info', 'white', 'dark blue'],
]

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
    'mark_all_as_read':       'A',
    'expand_visible_left':    'p',
    'expand_visible_right':   'n',
    'shrink_visible_left':    'P',
    'shrink_visible_right':   'N',

    # Tweets
    'tweet':                  't',
    'delete_tweet':           'X',
    'reply':                  'r',
    'retweet':                'R',
    'retweet_and_edit':       'E',
    'sendDM':                 'D',
    'update':                 'u',
    'tweet_hashtag':          'H',

    # Friendship
    'follow_selected':        'f',
    'unfollow_selected':      'U',

    # Favorites
    'fav':                    'b',
    'delete_fav':             'ctrl b',

    # Timelines
    'home':                   '.',
    'own_tweets':             '_',
    'favorites':              'B',
    'mentions':               'm',
    'DMs':                    'M',
    'search':                 '/',
    'search_user':            '@',
    'thread':                 'T',
    'hashtags':               'L',
    'user_timeline':          '+',

    # Meta
    'user_info':              'i',
    'help':                   '?',

    # Misc
    'quit':                   'q',
    'openurl':                'o',
    'redraw':                 'ctrl l',
}

params = {
    # TODO: refresh interval
    #'refresh':              2,
    # TODO: make time string configurable 
    #'relative_time':        1,
    'openurl_command':      'firefox',
    'logging_level':        3,
    'header_template':      ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'dm_template':          ' {sender_screen_name} => {recipient_screen_name} - {time} ',
}

#filter = {
    #'activate':         False,
    #'myself':           False,
    #'behavior':         'all',
    #'except':           [],
#}
