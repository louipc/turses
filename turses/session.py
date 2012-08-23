# -*- coding: utf-8 -*-

"""
The file with the session declarations is located on
``$HOME/.turses/sessions``.

``sessions`` is a ini-style configuration file in which each section represents
the layout of a session. The ``DEFAULT`` session is loaded when no other
section is present.

Each section has only two options:

    ``visible``
        contains the timelines that will be visible stacked in columns

    ``buffers``
        contains the timelines that won't be visible but will be loaded

For each option, you will define the timelines as a comma-separated list of
their names. Here is a list with the valid names:

 - ``home`` for the home timeline
 - ``mentions`` for the mentions timeline
 - ``favorites`` for the favorites timeline
 - ``messages`` for the direct message timeline
 - ``own_tweets`` for the timeline with your tweets

Here's an example of how the default section looks like:

.. code-block:: ini

    [DEFAULT]
    visible = home
    buffer = mentions, favorites, messages, own_tweets

Declaring a custom session is as easy as defining a section on the
``sessions`` file. As an example, let's define a session called
``interactions``, in which we would only like to view our mentions and messages
and load the home timeline in background:

.. code-block:: ini

    [interactions]
    visible = mentions, messages
    buffer = home

If you would like to load a session when starting ``turses``, you must provide
the name of the session as a command-line argument. You can start the session
named ``interactions`` by executing:

.. code-block:: sh

    $ turses -s interactions
    # or, alternatively
    $ turses --session interactions
"""

import re
from ConfigParser import RawConfigParser
from os import path
from functools import partial
from gettext import gettext as _

from turses.config import CONFIG_PATH
from turses.models import Timeline


SESSIONS_FILE = path.join(CONFIG_PATH, 'sessions')

invalid_name_re = re.compile(r'^\s*$')


def check_update_function_name(timeline, update_function_name=None):
    if not isinstance(timeline, Timeline):
        return False

    update_function = timeline.update_function
    if update_function is None:
        return False

    return update_function.__name__ == update_function_name

is_home_timeline = partial(check_update_function_name,
                           update_function_name='get_home_timeline')
is_mentions_timeline = partial(check_update_function_name,
                               update_function_name='get_mentions')
is_favorites_timeline = partial(check_update_function_name,
                               update_function_name='get_favorites')
is_own_timeline = partial(check_update_function_name,
                          update_function_name='get_own_timeline')
is_messages_timeline = partial(check_update_function_name,
                               update_function_name='get_direct_messages')


class TimelineFactory:
    def __init__(self, api):
        self.api = api

    def create(self, timeline_string):
        timeline = timeline_string.strip()

        if timeline == 'home':
            return Timeline(name=_('tweets'),
                            update_function=self.api.get_home_timeline,)
        elif timeline == 'mentions':
            return Timeline(name=_('mentions'),
                            update_function=self.api.get_mentions,)
        elif timeline == 'favorites':
            return Timeline(name=_('favorites'),
                            update_function=self.api.get_favorites,)
        elif timeline == 'messages':
            return Timeline(name=_('messages'),
                            update_function=self.api.get_direct_messages,)
        elif timeline == 'own_tweets':
            return Timeline(name=_('me'),
                            update_function=self.api.get_own_timeline,)


def clean_timeline_list_string(timeline_list_string):
    """
    Return a list with the timeline names encountered in
    `timeline_list_string`.
    """
    timeline_names = [name.strip() for name in timeline_list_string.split(',')]
    return [name.lower() for name in timeline_names if not invalid_name_re.match(name)]


class Session:
    """Load and save sessions."""

    def __init__(self, api):
        self.api = api
        self.factory = TimelineFactory(api)
        self.sessions = {
            'default': {
                'visible': 'home',
                'buffers': 'mentions, favorites, messages, own_tweets'
            },
        }

    def populate(self, timeline_list, session=None):
        """Populate `timeline_list` with the session timelines."""

        session_name = 'default' if session is None else session

        session_dict = self.sessions[session_name]

        visible_names = clean_timeline_list_string(session_dict['visible'])
        buffers_names = clean_timeline_list_string(session_dict['buffers'])

        # append first timeline (is always visible)
        first_timeline_name = visible_names.pop(0)
        first_timeline = self.factory.create(first_timeline_name)

        timeline_list.append_timeline(first_timeline)

        # append the rest of the visible timelines, expanding `timeline_list`
        # visible columns for showing the visible timelines
        for timeline_name in visible_names:
            timeline_list.append_timeline(self.factory.create(timeline_name))
            timeline_list.expand_visible_right()

        # append the rest of the timelines
        for timeline_name in buffers_names:
            timeline_list.append_timeline(self.factory.create(timeline_name))
