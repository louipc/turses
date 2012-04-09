# -*- coding: utf-8 -*-

"""
turses.constant
~~~~~~~~~~~~~~~

This module contains the programs defaults.
"""

palette = [
    ['body', 'default', '', 'standout'],
    ['focus','dark red', '', 'standout'],
    ['header', 'light blue', ''],
    ['line', 'dark blue', ''],
    ['active_tab', 'white', ''],
    ['visible_tab', 'light cyan', ''],
    ['inactive_tab', 'dark blue', ''],
    ['read', 'dark blue', ''],
    ['error', 'white', 'dark red'],
    ['info', 'white', 'dark blue'],
    ['favorited', 'yellow', ''],
    ['unread', 'dark red', ''],
    ['hashtag', 'dark green', ''],
    ['attag', 'brown', ''],
    ['highlight', 'dark red', ''],
    ['highlight_nick', 'light red', ''],
    ['help_bar', 'yellow', 'dark blue'],
    ['help_key', 'dark red', ''],
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
    'search_myself':          'ctrl u',
    'search_current_user':    'ctrl f',
    'thread':                 'T',
    'hashtags':               'L',

    # Meta
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
    'openurl_command':      'firefox',
    'open_image_command':   'feh',
    'transparency':         True,
    'activities':           True,
    'compact':              False,
    'help':                 True,
    'old_skool_border':     False,
    'box_position':         1,
    #'url_shorter':          'ur1ca',
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
