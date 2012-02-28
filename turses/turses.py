###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import random

import urwid
import twitter

from constant import palette
from widget import TabsWidget, TimelineBuffer, BufferFooter, TextEditor, TweetEditor
from api import Api
from timeline import Timeline, TimelineList
from help import HelpBuffer
from util import valid_status_text, valid_search_text


def _GetSampleUser():
    return twitter.User(id=718443,
                        name='Kesuke Miyagi',
                        screen_name='kesuke',
                        description=u'Canvas. JC Penny. Three ninety-eight.',
                        location='Okinawa, Japan',
                        url='https://twitter.com/kesuke',
                        profile_image_url='https://twitter.com/system/user/pro'
                                          'file_image/718443/normal/kesuke.pn'
                                          'g')

def _GetSampleStatus():
    return twitter.Status(created_at='Fri Jan 26 23:17:14 +0000 2007',
                          id=4391023,
                          text=u'A légpárnás hajóm tele van angolnákkal.',
                          user=_GetSampleUser())

def _dummy_status_list():
    """Returns a list of dummy statuses."""
    statuses = []
    for _ in xrange(0, random.randint(1, 11)):
        statuses.append(_GetSampleStatus())
    return statuses

class Turses(object):
    """Controller of the program."""

    def __init__(self, configuration):
        self.configuration = configuration
        self.api = Api(self.configuration.token[self.configuration.service]['consumer_key'],
                       self.configuration.token[self.configuration.service]['consumer_secret'],
                       self.configuration.oauth_token,
                       self.configuration.oauth_token_secret,)
        # default timelines
        self.timelines = TimelineList()
        self._append_home_timeline()
        self._append_mentions_timeline()
        self._append_favorites_timeline()
        self._append_direct_messages_timeline()
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

    def append_timeline(self, name, update_function, update_args=None):
        """
        Given a name, function to update a timeline and optionally
        arguments to the update function, it creates the timeline and
        appends it to `timelines`.
        """
        statuses = update_function()
        self.timelines.append_timeline(Timeline(name=name,
                                                statuses=statuses,                            
                                                update_function=update_function,
                                                update_function_args=update_args))


    def _append_home_timeline(self):
        self.append_timeline('Tweets', self.api.GetFriendsTimeline)

    def _append_mentions_timeline(self):
        self.append_timeline('Mentions', self.api.GetMentions)

    def _append_favorites_timeline(self):
        self.append_timeline('Favorites', self.api.GetFavorites)

    def _append_direct_messages_timeline(self):
        self.append_timeline('Direct Messages', self.api.GetDirectMessages)
        
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

    def key_handler(self, input):
        ch = ''.join(input)
        ##
        #  Motion commands
        ## 
        # Right
        if ch == self.configuration.keys['right'] or ch == 'right':
            self.next_timeline()
        # Left
        elif ch == self.configuration.keys['left'] or ch == 'left':
            self.previous_timeline()
        # Up
        elif ch == self.configuration.keys['up']:
            self.body.scroll_up()
        # Down
        elif ch == self.configuration.keys['down']:
            self.body.scroll_down()
        # Scroll to Top
        elif ch == self.configuration.keys['scroll_to_top']:
            raise NotImplemented
        # Scroll to Bottom
        elif ch == self.configuration.keys['scroll_to_bottom']:
            raise NotImplemented
        # Shift active buffer left
        elif ch == self.configuration.keys['shift_buffer_left']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_left()
                self._update_header()
        # Shift active buffer right
        elif ch == self.configuration.keys['shift_buffer_right']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_right()
                self._update_header()
        # Shift active buffer beggining
        elif ch == self.configuration.keys['shift_buffer_beggining']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_beggining()
                self._update_header()
        # Shift active buffer end
        elif ch == self.configuration.keys['shift_buffer_end']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_end()
                self._update_header()
        # Activate first buffer
        elif ch == self.configuration.keys['activate_first_buffer']:
            if self.timelines.has_timelines():
                self.timelines.activate_first()
                self._update_header()
                self.refresh_screen()
        # Activate last buffer
        elif ch == self.configuration.keys['activate_last_buffer']:
            if self.timelines.has_timelines():
                self.timelines.activate_last()
                self._update_header()
                self.refresh_screen()
        ##
        #  Action commands
        ##
        # Update
        elif ch == self.configuration.keys['update']:
            if self.timelines.has_timelines():
                self.timelines.update_active_timeline()
                self.refresh_screen()
        # Tweet
        elif ch == self.configuration.keys['tweet']:
            self.footer = TweetEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.tweet_handler)
        # Reply
        elif ch == self.configuration.keys['reply']:
            raise NotImplemented
        # Retweet
        elif ch == self.configuration.keys['retweet']:
            raise NotImplemented
        # Retweet and Edit
        elif ch == self.configuration.keys['retweet_and_edit']:
            raise NotImplemented
        # Delete buffer
        elif ch == self.configuration.keys['delete_buffer']:
            self.timelines.delete_active_timeline()
            if self.timelines.has_timelines():
                self.refresh_screen()
                self._update_header()
            else:
                # TODO help
                self.body.clear()
                self.header.set_tabs([''])
        # Delete tweet
        elif ch == self.configuration.keys['delete_tweet']:
            raise NotImplemented
        # Clear statuses
        elif ch == self.configuration.keys['clear']:
            self.body.clear()
        # Follow Selected
        elif ch == self.configuration.keys['follow_selected']:
            raise NotImplemented
        # Unfollow Selected
        elif ch == self.configuration.keys['unfollow_selected']:
            raise NotImplemented
        # Follow
        elif ch == self.configuration.keys['follow']:
            raise NotImplemented
        # Unfollow
        elif ch == self.configuration.keys['unfollow']:
            raise NotImplemented
        # Send Direct Message
        #FIXME
        #elif ch == self.configuration.keys['sendDM']:
            #self.api.direct_message()
        # Create favorite
        elif ch == self.configuration.keys['fav']:
            raise NotImplemented
        # Get favorite
        elif ch == self.configuration.keys['get_fav']:
            raise NotImplemented
        # Destroy favorite
        elif ch == self.configuration.keys['delete_fav']:
            raise NotImplemented
        # Open URL
        elif ch == self.configuration.keys['openurl']:
            raise NotImplemented
        # Open image
        elif ch == self.configuration.keys['open_image']:
            raise NotImplemented
        ##
        #  Timelines, Threads, User info, Help
        ##
        # Home Timeline
        elif ch == self.configuration.keys['home']:
            self._append_home_timeline()
        # Mention timeline
        elif ch == self.configuration.keys['mentions']:
            self._append_mentions_timeline()
        # Direct Message Timeline
        elif ch == self.configuration.keys['DMs']:
            self._append_direct_messages_timeline()
        # Search
        elif ch == self.configuration.keys['search']:
            self.footer = TextEditor(prompt='Search: ')
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.search_handler)
        # Search User
        elif ch == self.configuration.keys['search_user']:
            raise NotImplemented
        # Search Myself
        elif ch == self.configuration.keys['search_myself']:
            raise NotImplemented
        # Search Current User
        elif ch == self.configuration.keys['search_current_user']:
            raise NotImplemented
        # Thread
        elif ch == self.configuration.keys['thread']:
            raise NotImplemented
        # User info
        elif ch == self.configuration.keys['user_info']:
            raise NotImplemented
        # Help
        elif ch == self.configuration.keys['help']:
            self.show_help_buffer()
        ##
        #  Misc
        ##
        elif ch == self.configuration.keys['quit']:
            raise urwid.ExitMainLoop()
        elif ch == self.configuration.keys['redraw']:
            self.loop.draw_screen()
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
        # remove editor
        self.ui.set_focus('body')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.status_message('Tweet canceled')
            return
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
            self.status_message('Search canceled')
            return
        # append timeline
        tl_name = 'Search: %s' % text
        self.append_timeline(tl_name, self.api.GetSearch, text)
        # construct UI
        self._update_header()
        self.ui.set_focus('body')
        self.status_message('')

    def show_help_buffer(self):
        # TODO
        #  remove TL event handler, when closed enable it again
        self.status_message('Type <Esc> or q to leave the help page.')
        self.body = HelpBuffer(self.configuration)
        self.ui.set_body(self.body)
