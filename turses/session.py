# -*- coding: utf-8 -*-

"""
The file with the session declarations is located on
``$HOME/.turses/sessions``.

``sessions`` is a ini-style configuration file in which each section represents
the layout of a session. The ``defaults`` session is loaded when no other
section is present.

Each section has only two options:

    ``visible``
        contains the timelines that will be visible stacked in columns

    ``buffers``
        contains the timelines that won't be visible but will be loaded

.. warning:: The ``visible`` option must be present for any session but
   ``buffers`` is optional.

For each option, you will define the timelines as a comma-separated list of
their names. Here is a list with the valid names:

 - ``home`` for the home timeline
 - ``mentions`` for the mentions timeline
 - ``favorites`` for the favorites timeline
 - ``messages`` for the direct message timeline
 - ``own_tweets`` for the timeline with your tweets
 - ``search:<query>`` for searching timelines
 - ``hashtag:<query>`` for searching a hashtag
 - ``user:<screen_name>`` for a user's timeline
 - ``retweets_of_me`` for the timeline with your retweeted tweets

Declaring a custom session is as easy as defining a section on the
``sessions`` file. As an example, let's define a session called
``interactions``, in which we would only like to view our mentions, messages
and what people are saying about ``turses``; and load the home timeline in
background:

.. code-block:: ini

    [interactions]
    visible = mentions, messages, search:turses, hashtag:turses
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
import logging
from ConfigParser import RawConfigParser
from os import path
from gettext import gettext as _

from turses.api.helpers import (
    TimelineFactory,

    HOME_TIMELINE,
    MENTIONS_TIMELINE,
    FAVORITES_TIMELINE,
    MESSAGES_TIMELINE,
    OWN_TWEETS_TIMELINE,
)
from turses.config import (
    CONFIG_PATH,
    DEFAULT_SESSION,

    configuration,
)


SESSIONS_FILE = path.join(CONFIG_PATH, 'sessions')

VISIBLE = 'visible'
BUFFERS = 'buffers'

invalid_name_re = re.compile(r'^\s*$')


def clean_timeline_list_string(timeline_list_string):
    """
    Return a list with the timeline names encountered in
    `timeline_list_string`.
    """
    timeline_names = [name.strip() for name in timeline_list_string.split(',')]
    return [name.lower() for name in timeline_names if not invalid_name_re.match(name)]


class Session:
    """Loads and saves sessions."""

    def __init__(self, api):
        self.api = api
        self.factory = TimelineFactory(api)
        self.sessions_conf = RawConfigParser()
        self.sessions = {
            DEFAULT_SESSION: {
                VISIBLE: HOME_TIMELINE,
                BUFFERS: ', '.join([MENTIONS_TIMELINE,
                                    FAVORITES_TIMELINE,
                                    MESSAGES_TIMELINE,
                                    OWN_TWEETS_TIMELINE])
            }
        }
        if not path.isfile(SESSIONS_FILE):
            # create the sessions file
            logging.info(_('Sessions file created'))
            self.init_sessions_file()

    def init_sessions_file(self):
        """Create the `SESSIONS_FILE`."""
        self.sessions_conf.add_section(DEFAULT_SESSION)
        self.sessions_conf.set(DEFAULT_SESSION,
                               VISIBLE,
                               self.sessions[DEFAULT_SESSION][VISIBLE])
        self.sessions_conf.set(DEFAULT_SESSION,
                               BUFFERS,
                               self.sessions[DEFAULT_SESSION][BUFFERS])

        # create the file and write the `default` session
        with open(SESSIONS_FILE, 'w') as sessions_fp:
            self.sessions_conf.write(sessions_fp)

    def load_from_session_conf(self, session_name):
        """
        Load the session `session_name` from :attr:session_conf to
        :attr:sessions dictionary.
        """
        # we assume that the `visible` option is present
        visible = self.sessions_conf.get(session_name, VISIBLE)

        # `buffers` option is not required, prevent loading the default
        # buffers when the aforementioned option is not present
        if self.sessions_conf.has_option(session_name, BUFFERS):
            buffers = self.sessions_conf.get(session_name, BUFFERS)
        else:
            buffers = ''

        self.sessions[session_name] = {
            VISIBLE: visible,
            BUFFERS: buffers,
        }

    def populate(self, timeline_list, session=None):
        """Populate `timeline_list` with the session timelines."""
        session_name = configuration.session

        # read the `SESSIONS_FILE`
        self.sessions_conf.read(SESSIONS_FILE)

        if self.sessions_conf.has_section(session_name):
            self.load_from_session_conf(session_name)
            session_dict = self.sessions[session_name]
        else:
            # `configuration.session` does not exist, load default session
            session_dict = self.sessions[DEFAULT_SESSION]

        visible_names = session_dict[VISIBLE]
        buffers_names = session_dict[BUFFERS]

        self.append_visible_timelines(visible_names, timeline_list)
        self.append_background_timelines(buffers_names, timeline_list)

    def append_visible_timelines(self, visible_string, timeline_list):
        """"
        Given a `visible_string` with the names of the visible timelines,
        append them to `timeline_list` and make them all visible.
        """
        visible_names = clean_timeline_list_string(visible_string)

        # append first timeline (is always visible)
        first_timeline_name = visible_names.pop(0)
        first_timeline = self.factory(first_timeline_name)

        timeline_list.append_timeline(first_timeline)

        # append the rest of the visible timelines, expanding `timeline_list`
        # visible columns for showing the visible timelines
        for timeline_name in visible_names:
            timeline_list.append_timeline(self.factory(timeline_name))
            timeline_list.expand_visible_next()

    def append_background_timelines(self, buffers_string, timeline_list):
        """
        Given a `buffers_string` with the names of the timelines that should be
        loaded in the background, append them to `timeline_list`.
        """
        buffers_names = clean_timeline_list_string(buffers_string)

        for timeline_name in buffers_names:
            timeline_list.append_timeline(self.factory(timeline_name))
