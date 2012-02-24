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


# api
api = Api(consumer_key, consumer_secret, access_token_key, access_token_secret)
api.VerifyCredentials()

# timelines
friends_timeline = Timeline(api.GetFriendsTimeline())
another_timeline = Timeline([])

# buffers
friends_timeline_buffer = TimelineBuffer('Friends Timeline', friends_timeline)
another_timeline_buffer = TimelineBuffer('Another Timeline', another_timeline)

buffers = [friends_timeline_buffer, another_timeline_buffer]

top = BufferList(buffers)

def handle_input(input, raw):
    pressed = u''.join([unicode(i) for i in input])
    #show_key.set_text("Pressed " + pressed)
    if pressed == u'c':
        friends_timeline_buffer.clear()
    elif pressed == u'h':
        top.display_previous_buffer()
    elif pressed == u'l':
        top.display_next_buffer()
    return input

def exit_on_q(input):
    if input == 'q':
        raise urwid.ExitMainLoop()

loop = urwid.MainLoop(top, palette, 
                      input_filter=handle_input, unhandled_input=exit_on_q)
loop.run()
