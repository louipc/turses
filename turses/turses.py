###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

from credentials import *
from constant import palette
from widget import TimelineBuffer, BufferList
from api import Api
from timeline import Timeline
from keys import BufferListMotionKeyHandler
from managers import TimelineManager


class Turses(object):
    """Controller of the program."""
    def __init__(self):
        self.api = Api(consumer_key, 
                       consumer_secret, 
                       access_token_key, 
                       access_token_secret)

        self.init_timelines()

        # create UI
        friends_tl_buffer = TimelineBuffer('Tweets', friends_timeline)
        mention_tl_buffer = TimelineBuffer('Mentions', mentions)

        buffers = [friends_tl_buffer, mention_tl_buffer]

        self.buffer_list = BufferList(buffers)

        # motion key handler
        self.motion_key_handler = BufferListMotionKeyHandler(self.buffer_list)

        # start main loop
        self.update_all_timelines()
        loop = urwid.MainLoop(self.buffer_list, 
                              palette, 
                              input_filter=self.motion_key_handler.handle,
                              unhandled_input=self.action_key_handler,) 
        loop.run()

    def init_timelines(self):
        """Creates the default timelines."""
        self.timelines = []

        # tweets from friends
        friends_timeline = Timeline()
        friend_tl_manager = TimelineManager(friends_timeline, 
                                            self.api.GetFriendsTimeline)
        self.timelines.append(friend_tl_manager)
        
        # mentions
        mentions = Timeline()
        mention_tl_manager = TimelineManager(mentions, self.api.GetMentions)
        self.timelines.append(mention_tl_manager)

    def update_all_timelines(self):
        for timeline in self.timelines:
            timeline.update()

    def action_key_handler(self, input):
        """Handles keypresses that are not motion keys."""
        if input == 'r':
            self.update_all_timelines()
            self.buffer_list.update()
        

if __name__ == '__main__':
    Turses()
