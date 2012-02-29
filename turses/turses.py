###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


import urwid
import twitter

from constant import palette
from widget import TabsWidget, TimelineBuffer, Footer, TextEditor, TweetEditor, HelpBuffer
from api import Api
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text


class Turses(object):
    """Controller of the program."""

    def __init__(self, configuration):
        self.configuration = configuration
        # TODO: initialize API on background and render UI
        self.api = Api(self.configuration.token[self.configuration.service]['consumer_key'],
                       self.configuration.token[self.configuration.service]['consumer_secret'],
                       self.configuration.oauth_token,
                       self.configuration.oauth_token_secret,)
        # TODO make this configurable
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
        self.footer = Footer()
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
        
    def status_message(self, text):
        """Sets `text` as a status message on the footer."""
        if self.footer.__class__ is not Footer:
            self.footer = Footer()
        self.footer.message(text)
        self.ui.set_footer(self.footer)

    def clear_status(self):
        """Clears the status bar."""
        self.footer.clear()

    # -- Event handling -------------------------------------------------------

    def key_handler(self, input):
        ch = ''.join(input)
        
        # Motion commands
        motion_action = self._motion_key_handler(ch)
        if motion_action:
            return
        else:
            # check wether we are in a Help buffer
            if self.body.__class__ == HelpBuffer:
                # help only accepts motion commands and 'q'
                if ch == 'q':
                    self._timeline_mode()
                return

        # Buffer commands
        buffer_action = self._buffer_key_handler(ch)
        if buffer_action:
            return

        # Twitter commands
        twitter_action = self._twitter_key_handler(ch)
        if twitter_action:
            return

        # Turses commands
        turses_action = self._turses_key_handler(ch)
        if turses_action:
            return
        
        # Help
        elif ch == self.configuration.keys['help']:
            self._help_mode()
        ##
        #  Misc
        ##
        else:
            return input

    def _motion_key_handler(self, input):
        # Up
        if input == self.configuration.keys['up']:
            self.body.scroll_up()
        # Down
        elif input == self.configuration.keys['down']:
            self.body.scroll_down()
        # Scroll to Top
        elif input == self.configuration.keys['scroll_to_top']:
            self.body.scroll_top()
        # Scroll to Bottom
        elif input == self.configuration.keys['scroll_to_bottom']:
            self.body.scroll_bottom()

    def _buffer_key_handler(self, input):
        # Right
        if input == self.configuration.keys['right'] or input == 'right':
            self.next_timeline()
        # Left
        elif input == self.configuration.keys['left'] or input == 'left':
            self.previous_timeline()
        # Shift active buffer left
        elif input == self.configuration.keys['shift_buffer_left']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_left()
                self._update_header()
        # Shift active buffer right
        elif input == self.configuration.keys['shift_buffer_right']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_right()
                self._update_header()
        # Shift active buffer beggining
        elif input == self.configuration.keys['shift_buffer_beggining']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_beggining()
                self._update_header()
        # Shift active buffer end
        elif input == self.configuration.keys['shift_buffer_end']:
            if self.timelines.has_timelines():
                self.timelines.shift_active_end()
                self._update_header()
        # Activate first buffer
        elif input == self.configuration.keys['activate_first_buffer']:
            if self.timelines.has_timelines():
                self.timelines.activate_first()
                self._timeline_mode()
        # Activate last buffer
        elif input == self.configuration.keys['activate_last_buffer']:
            if self.timelines.has_timelines():
                self.timelines.activate_last()
                self._timeline_mode()
        # Delete buffer
        elif input == self.configuration.keys['delete_buffer']:
            self.timelines.delete_active_timeline()
            if self.timelines.has_timelines():
                self._timeline_mode()
            else:
                # TODO help
                self.body.clear()
                self.header.set_tabs([''])
        # Clear buffer
        elif input == self.configuration.keys['clear']:
            self.body.clear()

    def _twitter_key_handler(self, input):
        # Update timeline
        if input == self.configuration.keys['update']:
            if self.timelines.has_timelines():
                self.timelines.update_active_timeline()
                self._timeline_mode()
        # Tweet
        elif input == self.configuration.keys['tweet']:
            self.footer = TweetEditor()
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.tweet_handler)
        # Reply
        elif input == self.configuration.keys['reply']:
            # TODO retrieve twitter usernames pass them as `content`
            self.footer = TweetEditor(prompt='Reply: ', content='')
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.tweet_handler)
        # Retweet
        elif input == self.configuration.keys['retweet']:
            raise NotImplemented
        # Retweet and Edit
        elif input == self.configuration.keys['retweet_and_edit']:
            raise NotImplemented
        # Delete (own) tweet
        elif input == self.configuration.keys['delete_tweet']:
            raise NotImplemented
        # Follow Selected
        elif input == self.configuration.keys['follow_selected']:
            raise NotImplemented
        # Unfollow Selected
        elif input == self.configuration.keys['unfollow_selected']:
            raise NotImplemented
        # Follow
        elif input == self.configuration.keys['follow']:
            raise NotImplemented
        # Unfollow
        elif input == self.configuration.keys['unfollow']:
            raise NotImplemented
        # Send Direct Message
        #FIXME
        #elif input == self.configuration.keys['sendDM']:
            #self.api.direct_message()
        # Create favorite
        elif input == self.configuration.keys['fav']:
            raise NotImplemented
        # Get favorite
        elif input == self.configuration.keys['get_fav']:
            raise NotImplemented
        # Destroy favorite
        elif input == self.configuration.keys['delete_fav']:
            raise NotImplemented
        # Show home Timeline
        elif input == self.configuration.keys['home']:
            self._append_home_timeline()
        # Mention timeline
        elif input == self.configuration.keys['mentions']:
            self._append_mentions_timeline()
        # Direct Message Timeline
        elif input == self.configuration.keys['DMs']:
            self._append_direct_messages_timeline()
        # Search
        elif input == self.configuration.keys['search']:
            self.footer = TextEditor(prompt='search: ')
            self.ui.set_footer(self.footer)
            self.ui.set_focus('footer')
            urwid.connect_signal(self.footer, 'done', self.search_handler)
        # Ssearch User
        elif input == self.configuration.keys['search_user']:
            raise NotImplemented
        # Search Myself
        elif input == self.configuration.keys['search_myself']:
            raise NotImplemented
        # Search Current User
        elif input == self.configuration.keys['search_current_user']:
            raise NotImplemented
        # Thread
        elif input == self.configuration.keys['thread']:
            raise NotImplemented
        # User info
        elif input == self.configuration.keys['user_info']:
            raise NotImplemented

    def _external_program_handler(self, input):
        # Open URL
        if input == self.configuration.keys['openurl']:
            raise NotImplemented
        # Open image
        elif input == self.configuration.keys['open_image']:
            raise NotImplemented

    def _turses_key_handler(self, input):
        # Quit
        if input == self.configuration.keys['quit']:
            raise urwid.ExitMainLoop()
        # Redraw screen
        elif input == self.configuration.keys['redraw']:
            self.loop.draw_screen()

    def _timeline_mode(self):
        """Activates the Timeline mode."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            if self.body.__class__ == HelpBuffer:
                self.body = TimelineBuffer()
            self.body.render_timeline(active_timeline)
            self.ui.set_body(self.body)
            self._update_header()
        else:
            raise urwid.ExitMainLoopException


    def _help_mode(self):
        """Activates help mode."""
        self.status_message('Type <Esc> or q to leave the help page.')
        self.body = HelpBuffer(self.configuration)
        self.ui.set_body(self.body)

    def _update_header(self):
        self.header.set_tabs(self.timelines.get_timeline_names())
        self.header.set_active_tab(self.timelines.active_index)

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self._timeline_mode()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self._timeline_mode()

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
            self._timeline_mode()
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
        self.clear_status()
