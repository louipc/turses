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
 - ``search:<query>`` for search timelines
 - ``user:<screen_name>`` for a user's timeline
 - ``retweets_of_me`` for the timeline with your retweeted tweets

Declaring a custom session is as easy as defining a section on the
``sessions`` file. As an example, let's define a session called
``interactions``, in which we would only like to view our mentions, messages
and what people are saying about ``turses``; and load the home timeline in
background:

.. code-block:: ini

    [interactions]
    visible = mentions, messages, search:turses
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
from ConfigParser import RawConfigParser, NoSectionError
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
from turses.models import is_DM, Timeline


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
        self.sessions_conf = RawConfigParser(defaults={
                VISIBLE: HOME_TIMELINE,
                BUFFERS: ', '.join([MENTIONS_TIMELINE,
                                    FAVORITES_TIMELINE,
                                    MESSAGES_TIMELINE,
                                    OWN_TWEETS_TIMELINE,])
        })
        self.sessions = {
            DEFAULT_SESSION: dict(self.sessions_conf.defaults()),
        }

    def load(self):
        """Load sessions stored in `SESSIONS_FILE` to :attr:sessions."""
        if not path.isfile(SESSIONS_FILE):
            # create the sessions file
            logging.info(_('Sessions file created'))
            self.init_sessions_file()

        self.sessions_conf.read(SESSIONS_FILE)

        # load the non-default sessions
        for section in self.sessions_conf.sections():
            self.sections[section] = {
                VISIBLE: self.sessions_conf.get(section, VISIBLE),
                BUFFERS: self.sessions_conf.get(section, BUFFERS),
            }

        # load default session from `SESSIONS_FILE` if it's present since
        # `RawConfigParser.sections()` does not return the `DEFAULT` section
        self.sessions[DEFAULT_SESSION] = dict(self.sessions_conf.defaults())

    def init_sessions_file(self):
        """
        Create the `SESSIONS_FILE` and translate
        `turses.config.configuration.default_timelines` into a `default`
        session declaration.
        """
        # read default timelines from configuration for supporting legacy
        # timeline configuration
        default_timelines = configuration.default_timelines
        is_any_default_timeline = any((default_timelines[timeline] for timeline
                                                                   in DEFAULT_TIMELINES))
        default_visible = ''
        default_buffers_list = []

        if is_any_default_timeline:
            # the first timeline that is encountered is the only visible
            for timeline in DEFAULT_TIMELINES:
                if default_timelines[timeline]:
                    default_visible = timeline
                    break

            # the rest of the timelines are saved as buffers
            for timeline in DEFAULT_TIMELINES:
                if default_timelines[timeline] and not timeline in default_visible:
                    default_buffers_list.append(timeline)

        default_buffers = ', '.join(default_buffers_list)

        # update the default session according to the configuration
        self.sessions[DEFAULT_SESSION] = {
            VISIBLE: default_visible,
            BUFFERS: default_buffers,
        }

        self.sessions_conf.set(DEFAULT_SESSION, VISIBLE, default_visible)
        self.sessions_conf.set(DEFAULT_SESSION, BUFFERS, default_buffers)

        logging.debug('default visible: %s' % default_visible)
        logging.debug('default buffers: %s' % default_buffers)

        # create the file and write the `default` session
        with open(SESSIONS_FILE, 'w') as sessions_fp:
            self.sessions_conf.write(sessions_fp)

    def populate(self, timeline_list, session=None):
        """Populate `timeline_list` with the session timelines."""
        # TODO: validate that the session EXISTS
        session_name = configuration.session

        session_dict = self.sessions[session_name]

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
