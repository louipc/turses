###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid
import twitter

from credentials import *
from constant import palette
from widget import TabsWidget, TimelineBuffer, BufferFooter, TweetEditor
from api import Api
from timeline import Timeline, NamedTimelineList

# TODO move to utils
def valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= 140

def valid_search_text(text):
    """Checks the validity of a search text."""
    return text


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
        self.timelines.update_active_timeline()
        active_timeline = self.timelines.get_active_timeline()
        self.body.render_timeline(active_timeline)

    def status_message(self, text):
        self.footer = BufferFooter(text)
        self.ui.set_footer(self.footer)

    # -- Event handling -------------------------------------------------------

    # TODO
    def key_handler(self, input):
        clean_input = ''.join(input)
        if clean_input == 'e':
            self.footer = TweetEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.tweet_handler)
        elif clean_input == 's':
            self.footer = TweetEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.search_handler)
        elif clean_input == 'l':
            self.next_timeline()
        elif clean_input == 'h':
            self.previous_timeline()
        elif clean_input == 'r':
            self.refresh_timeline()
        elif clean_input == 'c':
            self.body.clear()
        elif clean_input == 't':
            import ipdb
            ipdb.set_trace()
        elif clean_input == 'q':
            raise urwid.ExitMainLoop
        else:
            return input

    def previous_timeline(self):
        self.timelines.activate_previous()
        self.header.activate_previous()
        self.refresh_timeline()

    def next_timeline(self):
        self.timelines.activate_next()
        self.header.activate_next()
        self.refresh_timeline()

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
            tweet = self.api.PostUpdate(text)
        except twitter.TwitterError:
            # FIXME `PostUpdate` ALWAYS raises this exception but
            #       it posts the tweet anyway.
            pass
        else:
            # TODO background
            self.refresh_timeline()
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
        tl_name = 'Search: %s' % text
        self.append_timeline(tl_name, self.api.GetSearch, text)
        # update header
        self.header.append_tab(tl_name)
        self.ui.set_focus('body')
            

if __name__ == '__main__':
    Turses()
