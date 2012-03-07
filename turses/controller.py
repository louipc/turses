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
from widget import WelcomeBuffer, TabsWidget, TimelineBuffer, Footer 
from widget import TextEditor, TweetEditor, HelpBuffer, DmEditor
from api import Api
from timeline import Timeline, TimelineList
from util import valid_status_text, valid_search_text, is_tweet, is_DM, is_retweet
from util import get_authors_username


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
        self.clear_status()
        self._timeline_mode()

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
        else:
            self._info_mode()
            self.clear_status()
        self.redraw_screen()

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
        timeline = Timeline(name=name,
                            update_function=update_function,
                            update_function_args=update_args) 
        timeline.update()
        self.timelines.append_timeline(timeline)

    def _append_home_timeline(self):
        self.append_timeline('Tweets', self.api.GetFriendsTimeline)

    def _append_mentions_timeline(self):
        self.append_timeline('Mentions', self.api.GetMentions)

    def _append_favorites_timeline(self):
        self.append_timeline('Favorites', self.api.GetFavorites)

    def _append_direct_messages_timeline(self):
        self.append_timeline('Direct Messages', self.api.GetDirectMessages)

    # -- Timeline mode --------------------------------------------------------

    # TODO decorator `timeline_mode` for checking `has_timelines`

    def previous_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_previous()
            self._timeline_mode()

    def next_timeline(self):
        if self.timelines.has_timelines():
            self.timelines.activate_next()
            self._timeline_mode()

    def shift_buffer_left(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_left()
            self._update_header()

    def shift_buffer_right(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_right()
            self._update_header()

    def shift_buffer_beggining(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_beggining()
            self._update_header()

    def shift_buffer_end(self):
        if self.timelines.has_timelines():
            self.timelines.shift_active_end()
            self._update_header()

    def activate_first_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_first()
            self._timeline_mode()

    def activate_last_buffer(self):
        if self.timelines.has_timelines():
            self.timelines.activate_last()
            self._timeline_mode()

    def delete_buffer(self):
        self.timelines.delete_active_timeline()
        if self.timelines.has_timelines():
            self._timeline_mode()
        else:
            self._info_mode()

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
        self.redraw_screen()

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

    def show_editor(self, 
                    editor_cls, 
                    done_signal_handler, 
                    prompt='', content='',
                    *args, **kwargs):
        # TODO add `cursor` parameter to set the cursor
        self.footer = editor_cls(prompt=prompt, content=content, *args, **kwargs)
        self.ui.set_footer(self.footer)
        self.ui.set_focus('footer')
        urwid.connect_signal(self.footer, 'done', done_signal_handler)

    def show_search_editor(self, prompt='', content=''):
        self.show_editor(TextEditor, 
                         self.search_handler, 
                         prompt=prompt, 
                         content=content)

    def show_tweet_editor(self, prompt='', content=''):
        """Shows the tweet editor and connects the 'done' signal."""
        self.show_editor(TweetEditor, 
                         self.tweet_handler, 
                         prompt=prompt, 
                         content=content)

    def show_dm_editor(self, prompt='', content=''):
        """Shows the DM editor and connects the 'done' signal."""
        status = self.body.get_focused_status()
        recipient = get_authors_username(status)
        if prompt == '':
            prompt = _('DM to %s' % recipient) 
        self.show_editor(DmEditor, 
                         self.dm_handler, 
                         prompt=prompt, 
                         content=content,
                         recipient=recipient,)

    def show_reply_editor(self):
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


    # -- Event handling -------------------------------------------------------

    def key_handler(self, input):
        """
        Handles the keyboard input that is not handled by the widgets by 
        default.
        """
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
                    self.clear_status()
                return

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
            self._help_mode()

    def _motion_key_handler(self, input):
        # TODO move handling of motion commands to the Widgets
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
            self.body.clear()

    def _twitter_key_handler(self, input):
        # Update timeline
        if input == self.configuration.keys['update']:
            self.update_active_timeline()
        # Tweet
        elif input == self.configuration.keys['tweet']:
            self.show_tweet_editor()
        # Reply
        elif input == self.configuration.keys['reply']:
            self.show_reply_editor()
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
            self.status_info_message('Still to implement!')
        # Create favorite
        elif input == self.configuration.keys['fav']:
            self.favorite()
        # Destroy favorite
        elif input == self.configuration.keys['delete_fav']:
            self.unfavorite()
        # Show home Timeline
        elif input == self.configuration.keys['home']:
            self._append_home_timeline()
        # Favorites timeline
        elif input == self.configuration.keys['favorites']:
            self._append_favorites_timeline()
        # Mention timeline
        elif input == self.configuration.keys['mentions']:
            self._append_mentions_timeline()
        # Direct Message timeline
        elif input == self.configuration.keys['DMs']:
            self._append_direct_messages_timeline()
        # Search
        elif input == self.configuration.keys['search']:
            self.show_search_editor()
        # Ssearch User
        elif input == self.configuration.keys['search_user']:
            self.status_info_message('Still to implement!')
        # Search Myself
        elif input == self.configuration.keys['search_myself']:
            self.status_info_message('Still to implement!')
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
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.tweet_handler)
        # remove editor
        self.ui.set_focus('body')
        self.status_info_message('sending tweet')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.status_info_message('Tweet canceled')
            return
        args = (text,)
        tweet_thread = Thread(target=self._tweet, args=args)
        tweet_thread.start()

    def dm_handler(self, username, text):
        """Handles the post as a DM of the given `text`."""
        # disconnect signal
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.dm_handler)
        # remove editor
        self.ui.set_focus('body')
        self.status_info_message('Sending DM')
        if not valid_status_text(text):
            # <Esc> was pressed
            self.status_info_message('DM canceled')
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
        urwid.disconnect_signal(self, self.ui.footer, 'done', self.search_handler)
        # remove editor
        self.ui.set_focus('body')
        self.status_info_message(_('Creating search timeline'))
        if not valid_search_text(text):
            # TODO error message editor and continue editing
            self.status_info_message('Search canceled')
            return
        # append timeline
        tl_name = 'Search: %s' % text                
        args = (tl_name, self.api.GetSearch, text)
        search_thread = Thread(target=self.append_timeline, args=args)
        search_thread.start()
        # construct UI
        self._update_header()
        self.ui.set_focus('body')
        self.clear_status()

    def retweet(self):
        status = self.body.get_focused_status()
        args = (status.id,)
        retweet_thread = Thread(target=self._retweet, args=args)
        retweet_thread.start()

    def manual_retweet(self):
        status = self.body.get_focused_status()
        rt_text = 'RT ' + status.text
        if valid_status_text(' ' + rt_text):
            self.show_tweet_editor(content=rt_text)
        else:
            self.status_error_message(_('Tweet too long for manual retweet'))

    def delete_tweet(self):
        status = self.body.get_focused_status()
        if is_tweet(status):
            args = (status.id,)
            delete_tweet_thread = Thread(target=self._delete_tweet, args=args)
            delete_tweet_thread.start()
        elif is_DM(status):
            self.status_error_message(_('Can not delete direct messages'))

    def follow_selected(self):
        status = self.body.get_focused_status()
        args = (status,)
        follow_thread = Thread(target=self._follow_status_author, args=args)
        follow_thread.start()

    def unfollow_selected(self):
        status = self.body.get_focused_status()
        args = (status,)
        unfollow_thread = Thread(target=self._unfollow_status_author, args=args)
        unfollow_thread.start()

    def favorite(self):
        status = self.body.get_focused_status()
        args = (status,)
        fav_thread = Thread(target=self._favorite, args=args)
        fav_thread.start()

    def unfavorite(self):
        status = self.body.get_focused_status()
        args = (status,)
        unfav_thread = Thread(target=self._unfavorite, args=args)
        unfav_thread.start()

    # Asynchronous API calls

    def _update_active_timeline(self):
        """Updates the timeline and renders the active timeline."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.get_active_timeline()
            active_timeline.update()
            if self.body.__class__ == TimelineBuffer:
                self._timeline_mode()
            self.status_info_message('%s updated' % active_timeline.name)

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
        #try:
            #self.api.PostDirectMessage(username, text)
        #except twitter.TwitterError, e:
            #self.status_error_message('%s' % e)
        #else:
            #self.status_info_message(_('DM to %s sent!' % username))
        pass


    def _follow_status_author(self, status):
        if is_retweet(status):
            # TODO search original twet author and follow
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

    def _unfollow_status_author(self, status):
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

    def _favorite(self, status):
        try:
            self.api.CreateFavorite(status)
            self.status_info_message(_('Tweet marked as favorite'))
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
