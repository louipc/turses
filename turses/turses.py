###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import argparse

import urwid
import twitter

from constant import palette
from widget import TabsWidget, TimelineBuffer, BufferFooter, TextEditor, TweetEditor
from api import Api
from timeline import Timeline, NamedTimelineList
from config import Configuration
from util import valid_status_text, valid_search_text

__version__ = 'alpha'


def arguments():
    """Parse all argument from the command line."""

    parser = argparse.ArgumentParser(
            "turses: a ncurses Twitter client written in Python.")
    parser.add_argument("-a", "--account",
            help="Use another account, store in a different file.")
    parser.add_argument("-c", "--config",
            help="Use another configuration file.")
    parser.add_argument("-g", "--generate-config",
            help="Generate a default configuration file.")
    parser.add_argument("-v", "--version", action="version", version="turses %s" % __version__,
            help="Show the current version of turses")
    args = parser.parse_args()
    return args


class Turses(object):
    """Controller of the program."""

    def __init__(self):
        self.configuration = Configuration(arguments())
        self.api = Api(self.configuration.token[self.configuration.service]['consumer_key'],
                       self.configuration.token[self.configuration.service]['consumer_secret'],
                       self.configuration.oauth_token,
                       self.configuration.oauth_token_secret,)
        self.timelines = NamedTimelineList()
        self.init_timelines()
        # create UI
        tl_names = self.timelines.get_timeline_names()
        self.header = TabsWidget(tl_names)
        self.timelines.update_active_timeline()
        self.body= TimelineBuffer(self.timelines.get_active_timeline())
        self.footer = BufferFooter()
        self.ui = urwid.Frame(self.body,
                              header=self.header,
                              footer=self.footer)
        # start main loop
        self.loop = urwid.MainLoop(self.ui,
                                   palette, 
                                   unhandled_input=self.key_handler,)
        self.loop.run()

    def init_timelines(self):
        """Initializes the timelines that appear by default."""
        # friends
        self.append_timeline('Tweets', self.api.GetFriendsTimeline)
        # mentions
        self.append_timeline('Mentions', self.api.GetMentions)
        # favorites
        self.append_timeline('Favorites', self.api.GetFavorites)
        # DMs
        self.append_timeline('Direct Messages', self.api.GetDirectMessages)
        

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

    def refresh_screen(self):
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            self.body.render_timeline(active_timeline)
        else:
            # TODO help
            pass

    def status_message(self, text):
        self.footer = BufferFooter(text)
        self.ui.set_footer(self.footer)

    # -- Event handling -------------------------------------------------------

    # TODO subsitute literals with configuration values
    def key_handler(self, input):
        clean_input = ''.join(input)
        if clean_input == 't':
            self.footer = TweetEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.tweet_handler)
        elif clean_input == 's':
            self.footer = TextEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.search_handler)
        elif clean_input == '<':
            if self.timelines.has_timelines():
                self.timelines.shift_active_left()
                self._update_header()
        elif clean_input == '>':
            if self.timelines.has_timelines():
                self.timelines.shift_active_right()
                self._update_header()
        elif clean_input == 'g':
            if self.timelines.has_timelines():
                self.timelines.activate_first()
                self._update_header()
                self.refresh_screen()
        elif clean_input == 'G':
            if self.timelines.has_timelines():
                self.timelines.activate_last()
                self._update_header()
                self.refresh_screen()
        elif clean_input == 'a':
            if self.timelines.has_timelines():
                self.timelines.shift_active_beggining()
                self._update_header()
        elif clean_input == 'e':
            if self.timelines.has_timelines():
                self.timelines.shift_active_end()
                self._update_header()
        elif clean_input == 'l':
            self.next_timeline()
        elif clean_input == 'h':
            self.previous_timeline()
        elif clean_input == 'r':
            if self.timelines.has_timelines():
                self.timelines.update_active_timeline()
                self.refresh_screen()
        elif clean_input == 'c':
            self.body.clear()
        elif clean_input == 'd':
            self.timelines.delete_active_timeline()
            if self.timelines.has_timelines():
                self.refresh_screen()
                self._update_header()
            else:
                # TODO help
                self.body.clear()
                self.header.set_tabs([''])
        elif clean_input == 'b':
            import ipdb
            ipdb.set_trace()
        elif clean_input == 'q':
            raise urwid.ExitMainLoop
        else:
            return input

    def _update_header(self):
        self.header.set_tabs(self.timelines.get_timeline_names())
        self.header.set_active_tab(self.timelines.active_index)

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self._update_header()
            self.refresh_screen()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self._update_header()
            self.refresh_screen()

    def tweet_handler(self, text):
        """Handles the post as a tweet of the given `text`."""
        # disconnect signal
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.tweet_handler)
        if not valid_status_text(text):
            # TODO error message editor and continue editing
            return
        self.ui.set_focus('body')
        self.status_message('Sending tweet')
        # API call
        try:
            self.api.PostUpdate(text)
        except twitter.TwitterError:
            # FIXME `PostUpdate` ALWAYS raises this exception but
            #       it posts the tweet anyway.
            pass
        else:
            # TODO background
            self.refresh_screen()
        finally:
            self.status_message('Tweet sent!')

    def search_handler(self, text):
        """
        Handles creating a timeline tracking the search term given in 
        `text`.
        """
        # disconnect signal
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.search_handler)
        if not valid_search_text(text):
            # TODO error message editor and continue editing
            return
        # append timeline
        tl_name = 'Search: %s' % text
        self.append_timeline(tl_name, self.api.GetSearch, text)
        # construct UI
        self._update_header()
        self.ui.set_focus('body')
        self.status_message('')
