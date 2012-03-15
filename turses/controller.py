###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


from gettext import gettext as _
from threading import Thread
from functools import partial

import urwid

from constant import palette
from api import Api
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text
from util import get_authors_username, get_mentioned_usernames


class Turses(object):
    """Controller of the program."""

    # -- Initialization -------------------------------------------------------

    def __init__(self, configuration, ui):
        self.configuration = configuration
        self.ui = ui
        # init API
        self.info_message(_('Initializing API'))
        consumer_key = self.configuration.token[self.configuration.service]['consumer_key'] 
        consumer_secret = self.configuration.token[self.configuration.service]['consumer_secret']
        oauth_token = self.configuration.oauth_token 
        oauth_token_secret = self.configuration.oauth_token_secret
        self.api = Api(consumer_key=consumer_key,
                       consumer_secret=consumer_secret,
                       access_token_key=oauth_token,
                       access_token_secret=oauth_token_secret,)
        self.api.init_api(callback=self.api_ready)
        # start main loop
        self.loop = urwid.MainLoop(self.ui,
                                   palette, 
                                   unhandled_input=self.key_handler,)
        self.loop.run()

    def init_timelines(self):
        self.info_message(_('Initializing timelines'))
        # note that API has to be initialized
        self.timelines = TimelineList()
        # TODO make default timeline list configurable
        # home
        self._append_home_timeline()
        # mentions
        self._append_mentions_timeline()
        # favorites
        self._append_favorites_timeline()
        # DMs
        self._append_direct_messages_timeline()
        # clear status
        self.clear_status()

    # -- Callbacks ------------------------------------------------------------

    def api_ready(self):
        self.info_message('API initialized')
        self.init_timelines()

    def tweet_sent(self):
        self.info_message(_('Tweet sent'))

    def retweet_posted(self):
        self.info_message(_('Retweet posted'))

    def status_deleted(self):
        self.update_active_timeline()
        self.info_message(_('Tweet deleted'))

    def follow_done(self, username=None):
        if username:
            self.info_message(_('You are now following %s' % username))

    def unfollow_done(self, username=None):
        self.update_active_timeline()
        if username:
            self.info_message(_('You no longer follow %s' % username))

    def tweet_favorited(self):
        self.info_message(_('Tweet marked as favorite'))

    def tweet_unfavorited(self):
        self.info_message(_('Tweet removed from favorites'))

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self):
        """
        Activates the Timeline mode if there are Timelines.
        
        If not, shows program info.
        """
        if self.timelines.has_timelines():
            self.draw_timelines()
        else:
            self.ui.info_mode()
            self.clear_status()
        self.redraw_screen()

    def info_mode(self):
        self.ui.info_mode()
        self.redraw_screen()

    def help_mode(self):
        """Activates help mode."""
        self.ui.help_mode(self.configuration)
        self.redraw_screen()

    # -- Timelines ------------------------------------------------------------

    def append_timeline(self, name, update_function, update_args=None):
        """
        Given a name, function to update a timeline and optionally
        arguments to the update function, it creates the timeline and
        appends it to `timelines`.
        """
        timeline = Timeline(name=name,
                            update_function=update_function,
                            update_function_args=update_args) 
        timeline.update()
        self.timelines.append_timeline(timeline)
        self.timeline_mode()

    def _append_home_timeline(self):
        self.append_timeline('Tweets', self.api.get_home_timeline)

    def _append_mentions_timeline(self):
        self.append_timeline('Mentions', self.api.get_mentions)

    def _append_favorites_timeline(self):
        self.append_timeline('Favorites', self.api.get_favorites)

    def _append_direct_messages_timeline(self):
        self.append_timeline('Direct Messages', self.api.get_direct_messages)

    # -- Timeline mode --------------------------------------------------------

    def draw_timelines(self):
        self.update_header()
        self.draw_timeline_buffer()

    def update_header(self):
        self.ui.update_header(self.timelines)
        # update tabs with buffer names, highlighting the active
        timeline_names = self.timelines.get_timeline_names()
        self.ui.set_tab_names(timeline_names)
        self.ui.activate_tab(self.timelines.active_index)

    def draw_timeline_buffer(self):
        # draw active timeline
        active_timeline = self.timelines.get_active_timeline()
        self.ui.draw_timeline(active_timeline)
        # redraw screen
        self.redraw_screen()

    # TODO decorator `timeline_mode` for checking `has_timelines` and drawing

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self.draw_timelines()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self.draw_timelines()

    def shift_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_left()
            self.draw_timelines()

    def shift_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_right()
            self.draw_timelines()

    def shift_buffer_beggining(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_beggining()
            self.draw_timelines()

    def shift_buffer_end(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_end()
            self.draw_timelines()

    def activate_first_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_first()
            self.draw_timelines()

    def activate_last_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_last()
            self.draw_timelines()

    def delete_buffer(self):
        self.timelines.delete_active_timeline()
        if self.timelines.has_timelines():
            self.draw_timelines()
        else:
            self.info_mode()

    # -- Footer ---------------------------------------------------------------
        
    def error_message(self, message):
        self.ui.status_error_message(message)
        self.redraw_screen()

    def info_message(self, message):
        self.ui.status_info_message(message)
        self.redraw_screen()

    def clear_status(self):
        """Clears the status bar."""
        self.ui.clear_status()
        self.redraw_screen()

    # -- UI -------------------------------------------------------------------

    def redraw_screen(self):
        # FIXME the position of the cursor is lost when redrawing screen
        if hasattr(self, "loop"):
            self.loop.draw_screen()

    # -- Twitter -------------------------------------------------------------- 

    def search(self, prompt='Search', content=''):
        self.ui.show_text_editor(prompt, content, self.search_handler)

    def tweet(self):
        self.ui.show_tweet_editor(prompt=_('Tweet'), 
                                  done_signal_handler=self.tweet_handler)

    def reply(self):
        status = self.ui.focused_status()
        author = get_authors_username(status)
        mentioned = get_mentioned_usernames(status)
        mentioned.insert(0, author)
        self.ui.show_tweet_editor(prompt=_('Reply to %s' % author),
                                  content=' '.join(mentioned),
                                  done_signal_handler=self.tweet_handler)

    def dm(self):
        # TODO
        pass

    #def show_dm_editor(self, prompt='', content=''):
        #"""Shows the DM editor and connects the 'done' signal."""
        #status = self.ui.focused_status()
        #recipient = get_authors_username(status)
        #if prompt == '':
            #prompt = _('DM to %s' % recipient) 
        #self.show_editor(DmEditor, 
                         #self.dm_handler, 
                         #prompt=prompt, 
                         #content=content,
                         #recipient=recipient,)


    # -- Event handling -------------------------------------------------------

    def key_handler(self, input):
        """
        Handles the keyboard input that is not handled by the widgets.
        """
        ch = ''.join(input)

        # Global commands
        turses_action = self._turses_key_handler(ch)
        # while in welcome buffer we can only view help, quit or redraw screen
        if turses_action:
            return

        # Timeline commands
        timeline_action = self._timeline_key_handler(ch)
        if timeline_action or self.ui.is_in_info_mode():
            return
        
        # Motion commands
        motion_action = self._motion_key_handler(ch)
        if motion_action:
            return

        # Help mode commands
        if self.ui.is_in_help_mode():
            # help only accepts motion commands and <Esc>
            if ch == 'esc':
                self.timeline_mode()
                self.clear_status()

        # Timeline mode commands
        if self.ui.is_in_timeline_mode():
            # Buffer commands
            buffer_action = self._buffer_key_handler(ch)
            if buffer_action:
                return

            # Twitter commands
            twitter_action = self._twitter_key_handler(ch)
            if twitter_action:
                return
            else:
                return input

    def _turses_key_handler(self, input):
        # Quit
        if input == self.configuration.keys['quit']:
            raise urwid.ExitMainLoop()
        # Redraw screen
        elif input == self.configuration.keys['redraw']:
            self.redraw_screen()
        # Help
        elif input == self.configuration.keys['help']:
            if self.ui.is_in_help_mode():
                pass
            else:
                self.help_mode()

    def _motion_key_handler(self, input):
        # TODO move handling of motion commands to the Widgets
        # Up
        if input == self.configuration.keys['up']:
            self.ui.body.scroll_up()
        # Down
        elif input == self.configuration.keys['down']:
            self.ui.body.scroll_down()
        # Scroll to Top
        elif input == self.configuration.keys['scroll_to_top']:
            self.ui.body.scroll_top()
        # Scroll to Bottom
        elif input == self.configuration.keys['scroll_to_bottom']:
            self.ui.body.scroll_bottom()

    def _buffer_key_handler(self, input):
        # Right
        if input == self.configuration.keys['right'] or input == 'right':
            self.next_timeline()
        # Left
        elif input == self.configuration.keys['left'] or input == 'left':
            self.previous_timeline()
        # Shift active buffer left
        elif input == self.configuration.keys['shift_buffer_left']:
            self.shift_buffer_left()
        # Shift active buffer right
        elif input == self.configuration.keys['shift_buffer_right']:
            self.shift_buffer_right()
        # Shift active buffer beggining
        elif input == self.configuration.keys['shift_buffer_beggining']:
            self.shift_buffer_beggining()
        # Shift active buffer end
        elif input == self.configuration.keys['shift_buffer_end']:
            self.shift_buffer_end()
        # Activate first buffer
        elif input == self.configuration.keys['activate_first_buffer']:
            self.activate_first_buffer()
        # Activate last buffer
        elif input == self.configuration.keys['activate_last_buffer']:
            self.activate_last_buffer()
        # Delete buffer
        elif input == self.configuration.keys['delete_buffer']:
            self.delete_buffer()
        # Clear buffer
        elif input == self.configuration.keys['clear']:
            self.ui.body.clear()

    def _timeline_key_handler(self, input):
        # Show home Timeline
        if input == self.configuration.keys['home']:
            home_thread = Thread(target=self._append_home_timeline)
            home_thread.start()
        # Favorites timeline
        elif input == self.configuration.keys['favorites']:
            favorites_thread = Thread(target=self._append_favorites_timeline)
            favorites_thread.start()
        # Mention timeline
        elif input == self.configuration.keys['mentions']:
            mentions_thread = Thread(target=self._append_mentions_timeline)
            mentions_thread.start()
        # Direct Message timeline
        elif input == self.configuration.keys['DMs']:
            direct_messages_thread = Thread(target=self._append_direct_messages_timeline)
            direct_messages_thread.start()
        # Search
        elif input == self.configuration.keys['search']:
            self.search()
        # Ssearch User
        elif input == self.configuration.keys['search_user']:
            self.info_message('Still to implement!')
        # Search Myself
        elif input == self.configuration.keys['search_myself']:
            self.info_message('Still to implement!')

    def _twitter_key_handler(self, input):
        # Update timeline
        if input == self.configuration.keys['update']:
            self.update_active_timeline()
        # Tweet
        elif input == self.configuration.keys['tweet']:
            self.tweet()
        # Reply
        elif input == self.configuration.keys['reply']:
            self.reply()
        # Retweet
        elif input == self.configuration.keys['retweet']:
            self.retweet()
        # Retweet and Edit
        elif input == self.configuration.keys['retweet_and_edit']:
            self.manual_retweet()
        # Delete (own) tweet
        elif input == self.configuration.keys['delete_tweet']:
            self.delete_tweet()
        # Follow Selected
        elif input == self.configuration.keys['follow_selected']:
            self.follow_selected()
        # Unfollow Selected
        elif input == self.configuration.keys['unfollow_selected']:
            self.unfollow_selected()
        # Send Direct Message
        elif input == self.configuration.keys['sendDM']:
            #self.show_dm_editor()
            self.info_message('Still to implement!')
        # Create favorite
        elif input == self.configuration.keys['fav']:
            self.favorite()
        # Destroy favorite
        elif input == self.configuration.keys['delete_fav']:
            self.unfavorite()
        # Search Current User
        elif input == self.configuration.keys['search_current_user']:
            self.info_message('Still to implement!')
        # Thread
        elif input == self.configuration.keys['thread']:
            self.info_message('Still to implement!')
        # User info
        elif input == self.configuration.keys['user_info']:
            self.info_message('Still to implement!')

    def _external_program_handler(self, input):
        # Open URL
        if input == self.configuration.keys['openurl']:
            self.info_message('Still to implement!')
        # Open image
        elif input == self.configuration.keys['open_image']:
            self.info_message('Still to implement!')

    # -- Twitter --------------------------------------------------------------

    def update_active_timeline(self):
        thread = Thread(target=self._update_active_timeline)
        thread.start()

    # Editor event handlers

    def tweet_handler(self, text):
        """Handles the post as a tweet of the given `text`."""
        # disconnect signal
        self.ui.remove_editor(self.tweet_handler)
        # status message
        self.ui.set_focus('body')
        self.info_message('sending tweet')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.info_message('Tweet canceled')
            return
        self.api.update(text, self.tweet_sent)

    def dm_handler(self, username, text):
        """Handles the post as a DM of the given `text`."""
        # disconnect signal
        self.ui.remove_editor(self.dm_handler)
        # remove editor
        self.ui.set_focus('body')
        self.info_message('Sending DM')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.info_message('DM canceled')
            return
        self.api.direct_message(username, text)

    def search_handler(self, text):
        """
        Handles creating a timeline tracking the search term given in 
        `text`.
        """
        # disconnect signal
        self.ui.remove_editor(self.search_handler)
        # remove editor
        self.ui.set_focus('body')
        if not valid_search_text(text):
            # TODO error message editor and continue editing
            self.info_message(_('Search canceled'))
            return
        else:
            self.info_message(_('Creating search timeline for "%s"' % text))
        # append timeline
        tl_name = 'Search: %s' % text                
        args = (tl_name, self.api.search, text)
        search_thread = Thread(target=self.append_timeline, 
                               args=args)
        search_thread.start()

    # -- API ------------------------------------------------------------------

    def retweet(self):
        status = self.ui.focused_status()
        self.api.retweet(status, self.retweet_posted)

    def manual_retweet(self):
        status = self.ui.focused_status()
        rt_text = 'RT ' + status.text
        if valid_status_text(' ' + rt_text):
            self.tweet(content=rt_text)
        else:
            self.error_message(_('Tweet too long for manual retweet'))

    def delete_tweet(self):
        status = self.ui.focused_status()
        self.api.destroy(status, self.status_deleted)

    def follow_selected(self):
        status = self.ui.focused_status()
        username = get_authors_username(status)
        follow_callback = partial(self.follow_done, username=username)
        self.api.create_friendship(username, follow_callback)

    def unfollow_selected(self):
        status = self.ui.focused_status()
        username = get_authors_username(status)
        unfollow_callback = partial(self.unfollow_done, username=username)
        self.api.destroy_friendship(username, unfollow_callback)

    def favorite(self):
        status = self.ui.focused_status()
        self.api.create_favorite(status, self.tweet_favorited)

    def unfavorite(self):
        status = self.ui.focused_status()
        self.api.destroy_favorite(status, self.tweet_unfavorited)

    # Asynchronous API calls

    def _update_active_timeline(self):
        """Updates the timeline and renders the active timeline."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            active_timeline.update()
            if self.ui.is_in_timeline_mode():
                self.draw_timelines()
            self.info_message('%s updated' % active_timeline.name)
