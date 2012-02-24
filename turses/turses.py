###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

from credentials import *
from constant import palette
from widget import TimelineBuffer, BufferHeader
from api import Api
from timeline import Timeline, NamedTimelineList
from managers import TimelineManager


class Turses(object):
    """Controller of the program."""

    def __init__(self):
        self.api = Api(consumer_key, 
                       consumer_secret, 
                       access_token_key, 
                       access_token_secret)
        self.timelines = NamedTimelineList()
        # tweets from friends
        tl_name = 'Tweets'
        tl = Timeline(update_function=self.api.GetFriendsTimeline)
        self.timelines.append_timeline(tl_name, tl)
        # mentions
        tl_name = 'Mentions'
        tl = Timeline(update_function=self.api.GetSearch, update_function_args='#python')
        self.timelines.append_timeline(tl_name, tl)
        # create UI
        self.timelines.update_all()
        self.ui = urwid.Frame(TimelineBuffer(self.timelines.get_active_timeline()),
                              header=BufferHeader([self.timelines.get_timeline_names()]))
        # start main loop
        self.loop = urwid.MainLoop(self.ui,
                                   palette, 
                                   input_filter=self.motion_key_handler,
                                   unhandled_input=self.action_key_handler,) 
        self.loop.run()

    def update_active_timeline(self):
        """Updates the active timeline and its representation."""
        # XXX TimelineManager
        self.timelines.update_all()

    def redraw_screen(self):
        self.loop.draw_screen()

    # TODO
    def motion_key_handler(self, input, raw):
        if input == 'l':
            pass
        elif input == 'r':
            pass
        else:
            return input

    def action_key_handler(self, input):
        """Handles keypresses that are not motion keys."""
        if input == 'r':
            # XXX separate thread
            self.update_active_timeline()
        elif input == 'c':
            # XXX clear timeline from `Turses`, not from `TimelineBuffer`
            self.buffer_list.clear_active_buffer()
        elif input == 'm':
            # mentions
            mentions = Timeline()
            mention_tl_manager = TimelineManager(mentions, self.api.GetMentions)
            self.timelines.append(mention_tl_manager)
            mention_tl_buffer = TimelineBuffer('Mentions', mentions)
            self.buffer_list.append_buffer(mention_tl_buffer)
            self.redraw_screen()
        elif input == 'a':
            self.buffer_list.display_previous_buffer()
            self.redraw_screen()
        elif input == 'd':
            self.buffer_list.display_next_buffer()
            self.redraw_screen()
        elif input == 't':
            import pdb
            pdb.set_trace()
        elif input == 'f':
            # favorites
            favorites = Timeline()
            favorite_tl_manager = TimelineManager(favorites, self.api.GetFavorites)
            self.timelines.append(favorite_tl_manager)
            favorite_tl_buffer = TimelineBuffer('Favorites', favorites)
            self.buffer_list.append_buffer(favorite_tl_buffer)
            self.redraw_screen()
        elif input == 'q':
            raise urwid.ExitMainLoop


if __name__ == '__main__':
    Turses()
