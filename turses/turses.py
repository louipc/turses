###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


import urllib2
from gettext import gettext as _
from threading import Thread

import urwid
import twitter

from constant import palette
from widget import WelcomeBuffer, TabsWidget, TimelineBuffer, Footer, TextEditor, TweetEditor, HelpBuffer
from api import Api
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text, is_tweet, is_DM, is_retweet


class Turses(object):
    """Controller of the program."""

    # -- Initialization -------------------------------------------------------

    def __init__(self, configuration):
        self.configuration = configuration
        # create UI
        self.header = TabsWidget()
        self.body = WelcomeBuffer()
        self.footer = Footer("[INFO] Initializing API")
        self.ui = urwid.Frame(self.body,
                              header=self.header,
                              footer=self.footer)
        # init API in background
        init_api_and_timelines = Thread(target=self.init_api)
        init_api_and_timelines.start()
        # start main loop
        self.loop = urwid.MainLoop(self.ui,
                                   palette, 
                                   unhandled_input=self.key_handler,)
        self.loop.run()

    def init_api(self):
        try:
            self.api = Api(self.configuration.token[self.configuration.service]['consumer_key'],
                           self.configuration.token[self.configuration.service]['consumer_secret'],
                           self.configuration.oauth_token,
                           self.configuration.oauth_token_secret,)
        except urllib2.URLError:
            self.status_error_message("Couldn't initialize API")
        else:
            self.init_timelines()

    def init_timelines(self):
        # note that API has to be initialized
        self.timelines = TimelineList()
        # TODO make default timeline list configurable
        self._append_home_timeline()
        self._append_mentions_timeline()
        self._append_favorites_timeline()
        self._append_direct_messages_timeline()
        self._timeline_mode()
        self.clear_status()

    # -- Modes ----------------------------------------------------------------

    def _timeline_mode(self):
        """
        Activates the Timeline mode if there are Timelines.
        
        If not, shows program info.
        """
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            self.body = TimelineBuffer()
            self.body.render_timeline(active_timeline)
            self.ui.set_body(self.body)
            self._update_header()
            self.redraw_screen()
        else:
            self._info_mode()
            self.clear_status()

    def _info_mode(self):
        """Shows program info."""
        self.header.clear()
        self.body = WelcomeBuffer()
        self.ui.set_body(self.body)

    def _help_mode(self):
        """Activates help mode."""
        self.status_info_message('Type <Esc> to leave the help page.')
        self.body = HelpBuffer(self.configuration)
        self.ui.set_body(self.body)

    # -- Timelines ------------------------------------------------------------

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

    # -- Timeline mode --------------------------------------------------------

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self._timeline_mode()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self._timeline_mode()

    # -- Header ---------------------------------------------------------------
    
    def _update_header(self):
        self.header.set_tabs(self.timelines.get_timeline_names())
        self.header.set_active_tab(self.timelines.active_index)

    # -- Footer ---------------------------------------------------------------
        
    def status_message(self, text):
        """Sets `text` as a status message on the footer."""
        if self.footer.__class__ is not Footer:
            self.footer = Footer()
        self.footer.message(text)
        self.ui.set_footer(self.footer)

    def status_error_message(self, message):
        self.status_message("[error] " + message)

    def status_info_message(self, message):
        self.status_message("[info] " + message)

    def clear_status(self):
        """Clears the status bar."""
        self.footer.clear()

    # -- UI -------------------------------------------------------------------

    def redraw_screen(self):
        self.loop.draw_screen()

    def show_editor(self, prompt='', content=''):
        pass

    def show_tweet_editor(self, prompt='', content=''):
        """Shows the tweet editor and connects the 'done' signal."""
        # TODO add `cursor` parameter to set the cursor
        self.footer = TweetEditor(prompt=prompt, content=content)
        self.ui.set_footer(self.footer)
        self.ui.set_focus('footer')
        urwid.connect_signal(self.footer, 'done', self.tweet_handler)

    # -- Event handling -------------------------------------------------------

    def key_handler(self, input):
        ch = ''.join(input)

        # Turses commands
        turses_action = self._turses_key_handler(ch)
        # while in welcome buffer we can only view help, quit or redraw screen
        if turses_action or self.body.__class__ == WelcomeBuffer:
            return
        
        # Motion commands
        motion_action = self._motion_key_handler(ch)
        if motion_action:
            return
        else:
            # check wether we are in a Help buffer
            if self.body.__class__ == HelpBuffer:
                # help only accepts motion commands and <Esc>
                if ch == 'esc':
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

        ##
        #  Misc
        ##
        else:
            return input

    def _turses_key_handler(self, input):
        # Quit
        if input == self.configuration.keys['quit']:
            raise urwid.ExitMainLoop()
        # Redraw screen
        elif input == self.configuration.keys['redraw']:
            self.loop.draw_screen()
        # Help
        elif input == self.configuration.keys['help']:
            self._help_mode()

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
                self._info_mode()
        # Clear buffer
        elif input == self.configuration.keys['clear']:
            self.body.clear()

    def _twitter_key_handler(self, input):
        # Update timeline
        if input == self.configuration.keys['update']:
            if self.timelines.has_timelines():
                update_thread = Thread(target=self.update_active_timeline)
                update_thread.start()
        # Tweet
        elif input == self.configuration.keys['tweet']:
            self.show_tweet_editor()
        # Reply
        elif input == self.configuration.keys['reply']:
            # TODO
            #  '@author_of_tweet <cursor> [@mentioned_author...]
            status = self.body.get_focused_status()
            if is_tweet(status):
                username = ''.join(['@', status.user.screen_name])
                is_username = lambda n: n.startswith('@') and n != username
                usernames = filter(is_username, status.text.split())
                usernames.insert(0, username)
                reply_text = ' '.join(usernames)
                # TODO filter own username
                # TODO set the cursor after `username`
                self.show_tweet_editor(prompt='Reply: ', content=reply_text)
            elif is_DM(status):
                # TODO
                pass
        # Retweet
        elif input == self.configuration.keys['retweet']:
            status = self.body.get_focused_status()
            try:
                # TODO make it in background and set status message
                #      'Retweet posted'
                self.status_info_message('Posting retweet...')
                self.api.PostRetweet(status.id)
            except twitter.TwitterError, e:
                self.status_error_message('%s' % e)
        # Retweet and Edit
        elif input == self.configuration.keys['retweet_and_edit']:
            status = self.body.get_focused_status()
            rt_text = 'RT ' + status.text
            if valid_status_text(' ' + rt_text):
                self.show_tweet_editor(content=rt_text)
            else:
                self.status_error_message('Tweet too long for manual retweet')
        # Delete (own) tweet
        elif input == self.configuration.keys['delete_tweet']:
            status = self.body.get_focused_status()
            if is_tweet(status):
                try:
                    self.api.DestroyStatus(status.id)
                    self.status_info_message(_('Tweet deleted'))
                    # TODO remove it from active_timeline, render_timeline,
                    #      and put the cursor on top of the deleted tweet
                except twitter.TwitterError:
                    self.status_error_message(_('You can delete your own tweets only'))
                except urllib2.URLError:
                    self.status_error_message(_('There was a problem with network communication, we can not ensure that the tweet has been deleted'))
        # Follow Selected
        elif input == self.configuration.keys['follow_selected']:
            status = self.body.get_focused_status()
            if is_retweet(status):
                # TODO
                pass
            elif is_tweet(status):
                username = status.user.screen_name
                try:
                    self.api.CreateFriendship(status.id)
                    self.status_info_message(_('You are now following @%s' % username))
                except twitter.TwitterError:
                    self.status_error_message(_('Twitter responded with an error, maybe you already follow @%s' % username))
                except urllib2.URLError:
                    self.status_error_message(_('There was a problem with network communication, we can not ensure that you are now following @%s' % username))
        # Unfollow Selected
        elif input == self.configuration.keys['unfollow_selected']:
            status = self.body.get_focused_status()
            if is_retweet(status):
                # TODO
                pass
            elif is_tweet(status):
                username = status.user.screen_name
                try:
                    self.api.DestroyFriendship(status.id)
                    self.status_info_message(_('You are no longer following @%s' % username))
                except twitter.TwitterError:
                    self.status_error_message(_('Twitter responded with an error, maybe you do not follow @%s' % username))
                except urllib2.URLError:
                    self.status_error_message(_('There was a problem with network communication, we can not ensure that you are not following @%s' % username))
        # Send Direct Message
        #FIXME
        #elif input == self.configuration.keys['sendDM']:
            #self.api.direct_message()
        # Create favorite
        elif input == self.configuration.keys['fav']:
            status = self.body.get_focused_status()
            raise NotImplemented
        # Get favorite
        elif input == self.configuration.keys['get_fav']:
            status = self.body.get_focused_status()
            raise NotImplemented
        # Destroy favorite
        elif input == self.configuration.keys['delete_fav']:
            status = self.body.get_focused_status()
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
            status = self.body.get_focused_status()
            raise NotImplemented
        # Search Myself
        elif input == self.configuration.keys['search_myself']:
            raise NotImplemented
        # Search Current User
        elif input == self.configuration.keys['search_current_user']:
            raise NotImplemented
        # Thread
        elif input == self.configuration.keys['thread']:
            status = self.body.get_focused_status()
            raise NotImplemented
        # User info
        elif input == self.configuration.keys['user_info']:
            status = self.body.get_focused_status()
            raise NotImplemented

    def _external_program_handler(self, input):
        # Open URL
        if input == self.configuration.keys['openurl']:
            raise NotImplemented
        # Open image
        elif input == self.configuration.keys['open_image']:
            raise NotImplemented

    # -- Twitter --------------------------------------------------------------

    def update_active_timeline(self):
        active_timeline = self.timelines.get_active_timeline()
        active_timeline.update()
        self._timeline_mode()

    def tweet_handler(self, text):
        """Handles the post as a tweet of the given `text`."""
        # disconnect signal
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.tweet_handler)
        # remove editor
        self.ui.set_focus('body')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.status_info_message('Tweet canceled')
            return
        self.status_info_message('Sending tweet')
        # TODO asynchronous API call
        try:
            self.api.PostUpdate(text)
        except twitter.TwitterError:
            # `PostUpdate` ALWAYS raises this exception but
            # it posts the tweet anyway.
            pass
        finally:
            self.status_info_message(_('Tweet sent!'))

    def search_handler(self, text):
        """
        Handles creating a timeline tracking the search term given in 
        `text`.
        """
        # disconnect signal
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.search_handler)
        if not valid_search_text(text):
            # TODO error message editor and continue editing
            self.status_info_message('Search canceled')
            return
        # append timeline
        tl_name = 'Search: %s' % text
        self.append_timeline(tl_name, self.api.GetSearch, text)
        # construct UI
        self._update_header()
        self.ui.set_focus('body')
        self.clear_status()
