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
from api import Api
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text, is_tweet, is_DM
from util import get_authors_username, get_mentioned_usernames
from ui import CursesInterface


class Turses(object):
    """Controller of the program."""

    # -- Initialization -------------------------------------------------------

    def __init__(self, configuration):
        self.configuration = configuration
        self.ui = CursesInterface()
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
            self.info_message(_('Initializing API'))
            self.api = Api(self.configuration.token[self.configuration.service]['consumer_key'],
                           self.configuration.token[self.configuration.service]['consumer_secret'],
                           self.configuration.oauth_token,
                           self.configuration.oauth_token_secret,)
        except urllib2.URLError:
            # TODO retry
            self.error_message(_('Couldn\'t initialize API'))
        else:
            self.init_timelines()

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

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self):
        """
        Activates the Timeline mode if there are Timelines.
        
        If not, shows program info.
        """
        if self.timelines.has_timelines():
            self.draw_timeline_buffer()
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
        self.draw_timeline_buffer()

    def _append_home_timeline(self):
        self.append_timeline('Tweets', self.api.GetFriendsTimeline)

    def _append_mentions_timeline(self):
        self.append_timeline('Mentions', self.api.GetMentions)

    def _append_favorites_timeline(self):
        self.append_timeline('Favorites', self.api.GetFavorites)

    def _append_direct_messages_timeline(self):
        self.append_timeline('Direct Messages', self.api.GetDirectMessages)

    # -- Timeline mode --------------------------------------------------------

    # TODO decorator `timeline_mode` for checking `has_timelines` and drawing

    def draw_timeline_buffer(self):
        # draw active timeline
        active_timeline = self.timelines.get_active_timeline()
        self.ui.draw_timeline(active_timeline)
        # update tabs with buffer names, highlighting the active
        timeline_names = self.timelines.get_timeline_names()
        self.ui.set_tab_names(timeline_names)
        self.ui.activate_tab(self.timelines.active_index)
        # redraw screen
        self.redraw_screen()

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self.draw_timeline_buffer()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self.draw_timeline_buffer()

    def shift_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_left()
            self.draw_timeline_buffer()

    def shift_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_right()
            self.draw_timeline_buffer()

    def shift_buffer_beggining(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_beggining()
            self.draw_timeline_buffer()

    def shift_buffer_end(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_end()
            self.draw_timeline_buffer()

    def activate_first_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_first()
            self.draw_timeline_buffer()

    def activate_last_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_last()
            self.draw_timeline_buffer()

    def delete_buffer(self):
        self.timelines.delete_active_timeline()
        if self.timelines.has_timelines():
            self.draw_timeline_buffer()
        else:
            self.info_mode()

    # -- Header ---------------------------------------------------------------
    
    def _update_header(self):
        self.ui.update_header(self.timelines)

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
                # FIXME
                raise Exception
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
            self.status_info_message('Still to implement!')
        # Search Myself
        elif input == self.configuration.keys['search_myself']:
            self.status_info_message('Still to implement!')

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
            self.status_info_message('Still to implement!')
        # Thread
        elif input == self.configuration.keys['thread']:
            self.status_info_message('Still to implement!')
        # User info
        elif input == self.configuration.keys['user_info']:
            self.status_info_message('Still to implement!')

    def _external_program_handler(self, input):
        # Open URL
        if input == self.configuration.keys['openurl']:
            self.status_info_message('Still to implement!')
        # Open image
        elif input == self.configuration.keys['open_image']:
            self.status_info_message('Still to implement!')

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
            self.ui.status_info_message('Tweet canceled')
            return
        args = (text,)
        tweet_thread = Thread(target=self._tweet, args=args)
        tweet_thread.start()

    def dm_handler(self, username, text):
        """Handles the post as a DM of the given `text`."""
        # disconnect signal
        self.ui.remove_editor(self.dm_handler)
        # remove editor
        self.ui.set_focus('body')
        self.status_info_message('Sending DM')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.ui.status_info_message('DM canceled')
            return
        args = (username, text,)
        dm_thread = Thread(target=self._direct_message, args=args)
        dm_thread.start()

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
        args = (tl_name, self.api.GetSearch, text)
        search_thread = Thread(target=self.append_timeline, 
                               args=args)
        search_thread.start()

    def retweet(self):
        status = self.ui.focused_status()
        args = (status.id,)
        retweet_thread = Thread(target=self._retweet, args=args)
        retweet_thread.start()

    def manual_retweet(self):
        status = self.ui.focused_status()
        rt_text = 'RT ' + status.text
        if valid_status_text(' ' + rt_text):
            self.tweet(content=rt_text)
        else:
            self.status_error_message(_('Tweet too long for manual retweet'))

    def delete_tweet(self):
        status = self.ui.focused_status()
        if is_tweet(status):
            args = (status.id,)
            delete_tweet_thread = Thread(target=self._delete_tweet, args=args)
            delete_tweet_thread.start()
        elif is_DM(status):
            self.status_error_message(_('Can not delete direct messages'))

    def follow_selected(self):
        status = self.ui.focused_status()
        args = (status,)
        follow_thread = Thread(target=self._follow_status_author, args=args)
        follow_thread.start()

    def unfollow_selected(self):
        status = self.ui.focused_status()
        args = (status,)
        unfollow_thread = Thread(target=self._unfollow_status_author, args=args)
        unfollow_thread.start()

    def favorite(self):
        status = self.ui.focused_status()
        args = (status,)
        fav_thread = Thread(target=self._favorite, args=args)
        fav_thread.start()

    def unfavorite(self):
        status = self.ui.focused_status()
        args = (status,)
        unfav_thread = Thread(target=self._unfavorite, args=args)
        unfav_thread.start()

    # Asynchronous API calls

    def _update_active_timeline(self):
        """Updates the timeline and renders the active timeline."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            active_timeline.update()
            if self.ui.is_in_timeline_mode():
                self.draw_timeline_buffer()
            self.ui.status_info_message('%s updated' % active_timeline.name)

    def _tweet(self, text):
        try:
            self.api.PostUpdate(text)
        except twitter.TwitterError, e:
            # `PostUpdate` ALWAYS raises this exception but
            # it posts the tweet anyway.
            self.status_error_message(_('%s' % e))
        finally:
            self.status_info_message(_('Tweet sent!'))

    def _retweet(self, id):
        try:
            self.status_info_message('Posting retweet...')
            self.api.PostRetweet(id)
        except twitter.TwitterError, e:
            self.status_error_message('%s' % e)

    def _delete_tweet(self, id):
        try:
            self.api.DestroyStatus(id)
            self.update_active_timeline()
            self.status_info_message(_('Tweet deleted'))
            # TODO remove it from active_timeline, render_timeline,
            #      and put the cursor on top of the deleted tweet
        except twitter.TwitterError, e:
            self.status_error_message('%s' % e)
        except urllib2.URLError:
            self.status_error_message(_('There was a problem with network communication, we can not ensure that the tweet has been deleted'))

    def _direct_message(self, username, text):
        # FIXME `httplib` launches a `BadStatusLine` exception
        try:
            self.api.PostDirectMessage(username, text)
        except twitter.TwitterError, e:
            self.status_error_message('%s' % e)
        else:
            self.status_info_message(_('DM to %s sent!' % username))

    def _follow_status_author(self, status):
        username = get_authors_username(status)
        try:
            self.api.CreateFriendship(username)
            self.status_info_message(_('You are now following @%s' % username))
        except twitter.TwitterError:
            self.status_error_message(_('Twitter responded with an error, maybe you already follow @%s' % username))
        except urllib2.URLError:
            self.status_error_message(_('There was a problem with network communication, we can not ensure that you are now following @%s' % username))

    def _unfollow_status_author(self, status):
        username = get_authors_username(status)
        try:
            self.api.DestroyFriendship(username)
            self.status_info_message(_('You are no longer following @%s' % username))
        except twitter.TwitterError:
            self.status_error_message(_('Twitter responded with an error, maybe you do not follow @%s' % username))
        except urllib2.URLError:
            self.status_error_message(_('There was a problem with network communication, we can not ensure that you are not following @%s' % username))

    def _favorite(self, status):
        try:
            self.api.CreateFavorite(status)
            self.status_info_message(_('Tweet marked as favorite'))
            # TODO: change `StatusWidget` attributes
        except twitter.TwitterError:
            self.status_error_message(_('Twitter responded with an error'))
        except urllib2.URLError:
            self.status_error_message(_('There was a problem with network communication, we can not ensure that you have favorited the tweet'))

    def _unfavorite(self, status):
        try:
            self.api.DestroyFavorite(status)
            self.status_info_message(_('Tweet deleted from favorites'))
        except twitter.TwitterError:
            self.status_error_message(_('Twitter responded with an error'))
        except urllib2.URLError:
            self.status_error_message(_('There was a problem with network communication, we can not ensure that you have unfavorited the tweet'))
