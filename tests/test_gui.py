###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('..')
from threading import Thread

import urwid

from credentials import *
from turses.api import Api
from turses.timeline import Timeline
from turses.widget import TimelineBuffer, BufferList, BufferHeader
from turses.constant import palette


class UpdateThread(Thread):
    def __init__(self, buffers):
        self.buffers = buffers
        Thread.__init__(self)

    def run(self):
        for buffer in self.buffers:
            buffer.update()


# api
api = Api(consumer_key, consumer_secret, access_token_key, access_token_secret)
api.VerifyCredentials()
# timelines
tweets = Timeline(update_function=api.GetUserTimeline)
timeline = Timeline(api.GetFriendsTimeline)
mentions = Timeline(update_function=api.GetMentions)
search = Timeline(update_function=api.GetSearch, update_function_args='#python')

# buffers
tweets_buffer = TimelineBuffer('tweets', tweets)
tl_buffer = TimelineBuffer('timeline', timeline)
mentions_buffer = TimelineBuffer('mentions', mentions)
search_buffer = TimelineBuffer('#python', search)

buffers = [tweets_buffer, tl_buffer, mentions_buffer, search_buffer]

top = BufferList(buffers)

def show_all_input(input, raw):
    pressed = u''.join([unicode(i) for i in input])
    #show_key.set_text("Pressed " + pressed)
    if pressed == u'l':
        top.next_buffer()
    elif pressed == u'h':
        top.prev_buffer()
    elif pressed == u'r':
        thread = UpdateThread(buffers)
        thread.run()
    elif pressed == u'd':
        top.remove_current_buffer()
    return input

def exit_on_cr(input):
    if input == 'tab':
        raise urwid.ExitMainLoop()

loop = urwid.MainLoop(top, palette, 
                      input_filter=show_all_input, unhandled_input=exit_on_cr)
loop.run()
