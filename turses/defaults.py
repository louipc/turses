# -*- coding: utf-8 -*-

"""
turses.defaults
~~~~~~~~~~~~~~~

This module contains the programs defaults.
"""

from gettext import gettext as _

# a list of (name, key, description) tuples with the default key bindings
key_bindings = {
    'motion': [
        ('up',                     'k', 
         _('scroll up')),
        ('down',                   'j', 
         _('scroll down')),
        ('left',                   'h', 
         _('activate the timeline on the left')),
        ('right',                  'l', 
         _('activate the timeline on the right')),
        ('scroll_to_top',          'g', 
         _('scroll to top')),
        ('scroll_to_bottom',       'G', 
         _('scroll to bottom')),
    ],

    'buffers': [
        ('activate_first_buffer',  'a', 
         _('activate first buffer')),
        ('activate_last_buffer',   'e', 
         _('activate last buffer')),
        ('shift_buffer_beggining', 'ctrl a', 
         _('shift active buffer to the beginning')),
        ('shift_buffer_end',       'ctrl e', 
         _('shift active buffer to the end')),
        ('shift_buffer_left',      '<', 
         _('shift active buffer one position to the left')),
        ('shift_buffer_right',     '>', 
         _('shift active buffer one position to the right')),
        ('expand_visible_left',    'p', 
         _('expand visible timelines one column to the left')),
        ('expand_visible_right',   'n', 
         _('expand visible timelines one column to the right')),
        ('shrink_visible_left',    'P', 
         _('shrink visible timelines one column from the left')),
        ('shrink_visible_right',   'N', 
         _('shrink visible timelines one column from the left')),
        ('delete_buffer',          'd', 
         _('delete buffer')),
        ('clear',                  'c', 
         _('clear status bar')),
        ('mark_all_as_read',       'A', 
         _('mark all tweets in the current timeline as read')),
    ],

    'tweets': [
        # Tweets
        ('tweet',                  't', 
         _('compose a tweet')),
        ('delete_tweet',           'X', 
         _('delete focused status')),
        ('reply',                  'r', 
         _('reply to focused status')),
        ('retweet',                'R', 
         _('retweet focused status')),
        ('retweet_and_edit',       'E', 
         _('open a editor for manually retweeting the focused status')),
        ('sendDM',                 'D', 
         _('compose a direct message')),
        ('update',                 'u', 
         _('refresh the active timeline')),
        ('tweet_hashtag',          'H', 
         _('compose a tweet with the same hashtags as the focused status')),
    ],

    'friendship': [
        ('follow_selected',        'f', 
         _('follow selected status\' author')),
        ('unfollow_selected',      'U', 
         _('unfollow selected status\' author')),
    ],

    'favorites': [
        ('fav',                    'b', 
         _('mark focused tweet as favorite')),
        ('delete_fav',             'ctrl b', 
         _('remove tweet from favorites')),
    ],

    'timelines': [
        ('home',                   '.', 
         _('open a home timeline')),
        ('own_tweets',             '_', 
         _('open a timeline with your tweets')),
        ('favorites',              'B', 
         _('open a timeline with your favorites')),
        ('mentions',               'm', 
         _('open a mentions timeline')),
        ('DMs',                    'M', 
         _('open a direct message timeline')),
        ('search',                 '/', 
         _('search for term and show resulting timeline')),
        ('search_user',            '@', 
         _('open a timeline with the tweets of the specified user')),
        ('user_timeline',          '+', 
         _('open a timeline with the tweets of the focused status\' author')),
        ('thread',                 'T', 
         _('open the thread of the focused status')),
        ('hashtags',               'L', 
         _('open a search timeline with the hashtags of the focused status')),
    ],

    'meta': [
        #('user_info',              'i', ''),
        ('help',                   '?', 
         _('show program help')),
    ],

    'turses': [
        ('quit',                   'q', 
         _('exit program')),
        ('openurl',                'o', 
         _('open URLs of the focused status in a browser')),
        ('redraw',                 'ctrl l', 
         _('redraw the screen')),
    ]
}

palette = [
    # Tabs
    ('active_tab',  'white', ''),
    ('visible_tab', 'light cyan', ''),
    ('inactive_tab', 'dark blue', ''),

    # Statuses
    ('header', 'light blue', ''),
    ('body', 'default', '', 'standout'),
    ('focus','dark red', '', 'standout'),
    ('line', 'dark blue', ''),
    ('unread', 'dark red', ''),
    ('read', 'dark blue', ''),
    ('favorited', 'yellow', ''),

    # Text
    ('highlight', 'dark red', ''),
    ('highlight_nick', 'light red', ''),
    ('attag', 'brown', ''),
    ('hashtag', 'dark green', ''),

    # Messages
    ('error', 'white', 'dark red'),
    ('info', 'white', 'dark blue'),
]

styles = {
    # TODO: make time string configurable 
    'header_template':      ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'dm_template':          ' {sender_screen_name} => {recipient_screen_name} - {time} ',
}

# Debug

# INFO logging level
logging_level = 3
