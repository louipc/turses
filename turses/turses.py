###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

from credentials import *
from constant import palette
from widget import TabsWidget, TimelineBuffer
from api import Api
from timeline import Timeline, NamedTimelineList


class Turses(object):
    """Controller of the program."""

    def __init__(self):
        self.api = Api(consumer_key, 
                       consumer_secret, 
                       access_token_key, 
                       access_token_secret)
        self.timelines = NamedTimelineList()
        self.init_timelines()
        # create UI
        tl_names = self.timelines.get_timeline_names()
        self.header = TabsWidget(tl_names)
        self.timelines.update_active_timeline()
        self.body= TimelineBuffer(self.timelines.get_active_timeline())
        self.ui = urwid.Frame(self.body,
                              header=self.header)
        # start main loop
        self.loop = urwid.MainLoop(self.ui,
                                   palette, 
                                   input_filter=self.motion_key_handler,
                                   unhandled_input=self.action_key_handler,) 
        self.loop.run()

    def init_timelines(self):
        """Initializes the timelines that appear by default."""
        # friends
        self.append_timeline('Tweets', self.api.GetFriendsTimeline)
        # mentions
        self.append_timeline('Mentions', self.api.GetMentions)
        # favorites
        self.append_timeline('Favorites', self.api.GetFavorites)

    def append_timeline(self, name, update_function, update_args=None):
        """
        Given a name, function to update a timeline and optionally
        arguments to the update function, it creates the timeline and
        appends it to `timelines`.
        """
        timeline =  update_function()
        self.timelines.append_timeline(name,
                                       Timeline(timeline,                            
                                                update_function=update_function,
                                                update_function_args=update_args))

    def refresh_timeline(self):
        active_timeline = self.timelines.get_active_timeline()
        self.body.render_timeline(active_timeline)

    # -- Event handling -------------------------------------------------------

    # TODO
    def motion_key_handler(self, input, raw):
        clean_input = ''.join(input)
        if clean_input == 'l':
            self.next_timeline()
        elif clean_input == 'h':
            self.previous_timeline()
        else:
            return input

    def up(self):
        pass

    def down(self):
        pass

    def previous_timeline(self):
        self.timelines.activate_previous()
        self.header.activate_previous()
        self.refresh_timeline()

    def next_timeline(self):
        self.timelines.activate_next()
        self.header.activate_next()
        self.refresh_timeline()

    def action_key_handler(self, input):
        """Handles keypresses that are not motion keys."""
        if input == 'r':
            self.refresh_timeline()
        elif input == 'c':
            self.body.clear()
        elif input == 't':
            import ipdb
            ipdb.set_trace()
        elif input == 'q':
            raise urwid.ExitMainLoop


if __name__ == '__main__':
    Turses()
