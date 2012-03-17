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
from api import AsyncApi
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text, is_valid_username
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
        self.api = AsyncApi(consumer_key=consumer_key,
                            consumer_secret=consumer_secret,
                            access_token_key=oauth_token,
                            access_token_secret=oauth_token_secret,)
        self.api.init_api(on_error=self.api_init_error,
                          on_success=self.init_timelines,)
        # start main loop
        try:
            self.main_loop()
        except:
            self.main_loop()
        else:
            # clear screen
            pass

    def main_loop(self):
        if not hasattr(self, 'loop'):
            self.loop = urwid.MainLoop(self.ui,
                                       palette, 
                                       unhandled_input=self.key_handler,)
        self.loop.run()

    def init_timelines(self):
        timelines_thread = Thread(target=self._init_timelines)
        timelines_thread.start()
    
    def _init_timelines(self):
        # API has to be authenticated
        while (not self.api.is_authenticated):
            pass
        self.info_message(_('Initializing timelines'))
        self.timelines = TimelineList()
        # TODO make default timeline list configurable
        self.append_default_timelines()
        self.update_all_timelines()
        self.info_message(_('Timelines loaded'))
        self.timeline_mode()

    # -- Callbacks ------------------------------------------------------------

    def api_init_error(self):
        # TODO retry
        self.error_message(_('Couldn\'t initialize API'))

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
        appends it to `timelines` asynchronously.
        """
        args = (name, update_function, update_args)
        thread = Thread(target=self._append_timeline, args=args)
        thread.start()

    def append_default_timelines(self):
        self.append_home_timeline()
        self.append_mentions_timeline()
        self.append_favorites_timeline()
        self.append_direct_messages_timeline()
        self.append_own_tweets_timeline()

    def append_home_timeline(self):
        self._append_timeline(name='Tweets',     
                              update_function=self.api.get_home_timeline)

    def append_own_tweets_timeline(self):
        user = self.api.verify_credentials()
        self._append_timeline(name='@%s' % user.screen_name,     
                              update_function=self.api.get_own_timeline)

    def append_mentions_timeline(self):
        self._append_timeline(name='Mentions',     
                              update_function=self.api.get_mentions)

    def append_favorites_timeline(self):
        self._append_timeline(name='Favorites',     
                              update_function=self.api.get_favorites)

    def append_direct_messages_timeline(self):
        self._append_timeline(name='DMs',
                              update_function=self.api.get_direct_messages)

    def _append_timeline(self, name, update_function, update_args=None):
        timeline = Timeline(name=name,
                            update_function=update_function,
                            update_function_args=update_args) 
        self.timelines.append_timeline(timeline)

    def update_all_timelines(self):
        for timeline in self.timelines:
            timeline.update()
        self.info_message(_('%s updated' % timeline.name))

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
        ## redraw screen
        #self.redraw_screen()

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
        self.ui.footer.error_message(message)
        self.redraw_screen()

    def info_message(self, message):
        self.ui.footer.info_message(message)
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

    def search(self):
        self.ui.show_text_editor(prompt='Search', 
                                 done_signal_handler=self.search_handler)

    def search_user(self):
        self.ui.show_text_editor(prompt=_('Search user (no need to prepend it with "@")'),
                                 content='',
                                 done_signal_handler=self.search_user_handler)

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
            home_thread = Thread(target=self.append_home_timeline)
            home_thread.start()
        # Own tweets
        elif input == self.configuration.keys['own_tweets']:
            own_tweets_thread = Thread(target=self.append_own_tweets_timeline)
            own_tweets_thread.start()
        # Favorites timeline
        elif input == self.configuration.keys['favorites']:
            favorites_thread = Thread(target=self.append_favorites_timeline)
            favorites_thread.start()
        # Mention timeline
        elif input == self.configuration.keys['mentions']:
            mentions_thread = Thread(target=self.append_mentions_timeline)
            mentions_thread.start()
        # Direct Message timeline
        elif input == self.configuration.keys['DMs']:
            direct_messages_thread = Thread(target=self.append_direct_messages_timeline)
            direct_messages_thread.start()
        # Search
        elif input == self.configuration.keys['search']:
            self.search()
        # Ssearch User
        elif input == self.configuration.keys['search_user']:
            #self.info_message('Still to implement!')
            self.search_user()
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
        update_thread = Thread(target=self._update_active_timeline)
        update_thread.start()

    def _update_active_timeline(self):
        """Updates the timeline and renders the active timeline."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            active_timeline.update()
            if self.ui.is_in_timeline_mode():
                self.draw_timelines()
            self.info_message('%s updated' % active_timeline.name)

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
        # API call
        tweet_sent = partial(self.info_message, _('Tweet sent'))
        tweet_not_sent = partial(self.error_message, _('Tweet not sent'))
        self.api.update(text=text, 
                        on_success=tweet_sent,
                        on_error=tweet_not_sent,)

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
        self.api.direct_message(screen_name=username, 
                                text=text)

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
            self.info_message(_('Search cancelled'))
            return
        else:
            self.info_message(_('Creating search timeline for "%s"' % text))
        # append timeline
        timeline = Timeline(name='Search: %s' % text,
                            update_function=self.api.search, 
                            update_function_args=text)
        timeline.update()
        self.timelines.append_timeline(timeline)
        self.draw_timelines()
        self.info_message(_('Search timeline for "%s" created' % text))

    def search_user_handler(self, username):
        """
        Handles creating a timeline tracking the searched user's tweets.
        """
        # disconnect signal
        self.ui.remove_editor(self.search_user_handler)
        # remove editor
        self.ui.set_focus('body')
        if not is_valid_username(username):
            # TODO error message editor and continue editing
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Fetching latest tweets from @%s' % username))
        # append timeline
        timeline = Timeline(name='@%s' % username,
                            update_function=self.api.get_user_timeline, 
                            update_function_args=username,)
        timeline.update()
        self.timelines.append_timeline(timeline)
        self.draw_timelines()
        self.info_message(_('@%s timeline created' % username))

    # -- API ------------------------------------------------------------------

    def retweet(self):
        status = self.ui.focused_status()
        retweet_posted = partial(self.info_message, 
                                 _('Retweet posted'))
        retweet_post_failed = partial(self.error_message, 
                                      _('Failed to post retweet'))
        self.api.retweet(on_error=retweet_post_failed,
                         on_success=retweet_posted,
                         status=status,)

    def manual_retweet(self):
        status = self.ui.focused_status()
        rt_text = 'RT ' + status.text
        if valid_status_text(' ' + rt_text):
            self.tweet(content=rt_text)
        else:
            self.error_message(_('Tweet too long for manual retweet'))

    def delete_tweet(self):
        status = self.ui.focused_status()
        status_deleted = partial(self.info_message, 
                                 _('Tweet deleted'))
        status_not_deleted = partial(self.error_message, 
                                     _('Failed to delete tweet'))
        self.api.destroy(status=status, 
                         on_error=status_not_deleted,
                         on_success=status_deleted)

    def follow_selected(self):
        status = self.ui.focused_status()
        username = get_authors_username(status)
        follow_done = partial(self.info_message, 
                              _('You are now following %s' % username))
        follow_error = partial(self.error_message, 
                               _('We can not ensure that you are following %s' % username))
        self.api.create_friendship(screen_name=username, 
                                   on_error=follow_error,
                                   on_success=follow_done)

    def unfollow_selected(self):
        status = self.ui.focused_status()
        username = get_authors_username(status)
        unfollow_done = partial(self.info_message, 
                                _('You are no longer following %s' % username))
        unfollow_error = partial(self.error_message, 
                               _('We can not ensure that you are not following %s' % username))
        self.api.destroy_friendship(screen_name=username, 
                                    on_error=unfollow_error,
                                    on_success=unfollow_done)

    def favorite(self):
        status = self.ui.focused_status()
        favorite_error = partial(self.error_message,
                                 _('Failed to mark tweet as favorite'))
        favorite_done = partial(self.info_message,
                                _('Tweet marked as favorite'))
        self.api.create_favorite(status=status, 
                                 on_error=favorite_error,
                                 on_success=favorite_done)

    def unfavorite(self):
        status = self.ui.focused_status()
        unfavorite_error = partial(self.error_message,
                                   _('Failed to remove tweet from favorites'))
        unfavorite_done = partial(self.info_message,
                                  _('Tweet removed from favorites'))
        self.api.destroy_favorite(status=status, 
                                  on_error=unfavorite_error,
                                  on_success=unfavorite_done)
