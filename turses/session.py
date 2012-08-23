# -*- coding: utf-8 -*-

"""
This module contains the logic to load and save sessions.
"""

from gettext import gettext as _

from turses.models import Timeline


class Session:
    """Load and save sessions."""

    def __init__(self, api):
        self.api = api

    def populate(self, timeline_list):
        """Populate `timeline_list` with the session timelines."""

        home_timeline = Timeline(name=_('tweets'),
                                 update_function=self.api.get_home_timeline,)
        mentions_timeline = Timeline(name=_('mentions'),
                                     update_function=self.api.get_mentions,)
        favorites_timeline = Timeline(name=_('favorites'),
                                      update_function=self.api.get_favorites,)
        messages_timeline = Timeline(name=_('messages'),
                                      update_function=self.api.get_direct_messages,)
        own_timeline = Timeline(name=_('@'),
                                update_function=self.api.get_own_timeline,)

        timeline_list.append_timeline(home_timeline)
        timeline_list.append_timeline(mentions_timeline)
        timeline_list.append_timeline(favorites_timeline)
        timeline_list.append_timeline(messages_timeline)
        timeline_list.append_timeline(own_timeline)
