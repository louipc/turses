# -*- coding: utf-8 -*-

"""
This module contains the controller and key handling logic of turses.
"""

import logging
from gettext import gettext as _
from functools import partial, wraps
import webbrowser

import urwid
from tweepy import TweepError

from turses.utils import get_urls
from turses.meta import async, wrap_exceptions, Observer
from turses.config import (
        HOME_TIMELINE,
        MENTIONS_TIMELINE,
        FAVORITES_TIMELINE,
        MESSAGES_TIMELINE,
        OWN_TWEETS_TIMELINE,

        configuration,
)
from turses.utils import is_username
from turses.models import (
        is_DM,
        is_valid_status_text,
        is_valid_search_text,
        sanitize_username,

        Timeline,
        TimelineList,
)
from turses.api.base import AsyncApi


def merge_dicts(*args):
    """
    Merge all dictionaries given as positional arguments in a single
    dictionary.
    """
    result = {}
    for arg in args:
        result.update(arg)
    return result


class KeyHandler(object):
    """
    Maps key bindings from configuration to calls to :class:`Controller`
    functions.
    """

    def __init__(self, controller):
        self.controller = controller

        self.TURSES_COMMANDS = {
            'quit':          self.controller.exit,
            'redraw':        self.controller.redraw_screen,
            'help':          self.controller.help_mode,
            'reload_config': self.controller.reload_configuration,
            'clear':         self.controller.clear_status,
        }

        self.MOTION_COMMANDS = {
            'up':               self.controller.scroll_up,
            'down':             self.controller.scroll_down,
            'scroll_to_top':    self.controller.scroll_top,
            'scroll_to_bottom': self.controller.scroll_bottom,
        }

        self.BUFFER_COMMANDS = {
            'right':                  self.controller.next_timeline,
            'left':                   self.controller.previous_timeline,

            'shift_buffer_left':      self.controller.shift_buffer_left,
            'shift_buffer_right':     self.controller.shift_buffer_right,
            'shift_buffer_beggining': self.controller.shift_buffer_beggining,
            'shift_buffer_end':       self.controller.shift_buffer_end,

            'expand_visible_left':    self.controller.expand_buffer_left,
            'expand_visible_right':   self.controller.expand_buffer_right,
            'shrink_visible_left':    self.controller.shrink_buffer_left,
            'shrink_visible_right':   self.controller.shrink_buffer_right,

            'activate_first_buffer':  self.controller.activate_first_buffer,
            'activate_last_buffer':   self.controller.activate_last_buffer,

            'delete_buffer':          self.controller.delete_buffer,
            'mark_all_as_read':       self.controller.mark_all_as_read,
        }

        self.TIMELINE_COMMANDS = {
            'home':           self.controller.append_home_timeline,
            'own_tweets':     self.controller.append_own_tweets_timeline,
            'favorites':      self.controller.append_favorites_timeline,
            'mentions':       self.controller.append_mentions_timeline,
            'DMs':            self.controller.append_direct_messages_timeline,
            'search':         self.controller.search,
            'search_user':    self.controller.search_user,
            'thread':         self.controller.append_thread_timeline,
            'user_info':      self.controller.user_info,
            'hashtags':       self.controller.search_hashtags,
            'user_timeline':  self.controller.focused_status_author_timeline,
            'retweets_of_me': self.controller.append_retweets_of_me_timeline,
        }

        self.TWITTER_COMMANDS = {
            'update':            self.controller.update_active_timeline,
            'update_all':        self.controller.update_all_timelines,
            'tweet':             self.controller.tweet,
            'reply':             self.controller.reply,
            'retweet':           self.controller.retweet,
            'retweet_and_edit':  self.controller.manual_retweet,
            'delete_tweet':      self.controller.delete_tweet,
            'follow_selected':   self.controller.follow_selected,
            'follow_user':       self.controller.follow_user,
            'unfollow_selected': self.controller.unfollow_selected,
            'unfollow_user':     self.controller.unfollow_user,
            'send_dm':           self.controller.direct_message,
            'fav':               self.controller.favorite,
            'delete_fav':        self.controller.unfavorite,
            'tweet_hashtag':     self.controller.tweet_with_hashtags,
        }

        self.EXTERNAL_PROGRAM_COMMANDS = {
            'openurl':         self.controller.open_urls,
            'open_status_url': self.controller.open_status_url,
        }

        # commands grouped by modes
        all_commands = [self.TURSES_COMMANDS,
                        self.MOTION_COMMANDS,
                        self.BUFFER_COMMANDS,
                        self.TIMELINE_COMMANDS,
                        self.TWITTER_COMMANDS,
                        self.EXTERNAL_PROGRAM_COMMANDS]

        # Timeline mode
        self.TIMELINE_MODE_COMMANDS = merge_dicts(*all_commands)

        # Info mode
        self.INFO_MODE_COMMANDS = merge_dicts(self.TURSES_COMMANDS,
                                              self.TIMELINE_COMMANDS)

        # Help mode
        self.HELP_MODE_COMMANDS = merge_dicts(self.TURSES_COMMANDS,
                                              self.MOTION_COMMANDS)

    def command(self, key):
        """
        Return the command name that corresponds to `key` (if any).
        """
        for command_name in configuration.key_bindings:
            bound_key, _ = configuration.key_bindings[command_name]
            if key == bound_key:
                return command_name

    def handle(self, key):
        """Handle keyboard input."""
        command = self.command(key)

        # Editor mode -- don't interpret keypress as command
        if self.controller.is_in_editor_mode():
            return self.controller.forward_to_editor(key)

        # User info mode
        #  we remove the user widget and activate timeline mode when
        #  receiving input
        if self.controller.is_in_user_info_mode():
            self.controller.timeline_mode()

        # Help mode
        if self.controller.is_in_help_mode():
            # <Esc> in Help mode is not associated with a command
            if key == 'esc':
                return self.controller.timeline_mode()
            elif command in self.HELP_MODE_COMMANDS:
                handler = self.HELP_MODE_COMMANDS[command]
                return handler()
        # Info mode
        elif self.controller.is_in_info_mode():
            if command in self.INFO_MODE_COMMANDS:
                handler = self.INFO_MODE_COMMANDS[command]
                return handler()
        # Timeline mode
        elif self.controller.is_in_timeline_mode():
            if command in self.TIMELINE_MODE_COMMANDS:
                handler = self.TIMELINE_MODE_COMMANDS[command]
                return handler()

        return key


# Decorators


def has_active_status(func):
    """
    `func` only is executed if there is a active status.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        status = self.timelines.active_status
        if status != None:
            return func(self, *args, **kwargs)
    return wrapper

def has_timelines(func):
    """
    `func` only is executed if there are any timelines.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.timelines.has_timelines():
            return func(self, *args, **kwargs)
    return wrapper


def text_from_editor(func):
    """
    `func` receives text from an editor.
    """
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.ui.hide_editor(wrapper)
        self.timeline_mode()
        return func(self, *args, **kwargs)

    return wrapper


# Controller


class Controller(Observer):
    """
    The :class:`Controller`.
    """

    # Modes

    INFO_MODE = 0
    TIMELINE_MODE = 1
    HELP_MODE = 2
    EDITOR_MODE = 3
    USER_INFO_MODE = 4

    # -- Initialization -------------------------------------------------------

    def __init__(self, ui, api_backend):
        self.ui = ui
        self.editor = None

        # Model
        self.timelines = TimelineList()
        self.timelines.subscribe(self)

        # Mode
        self.mode = self.INFO_MODE

        # API
        oauth_token = configuration.oauth_token
        oauth_token_secret = configuration.oauth_token_secret
        self.api = AsyncApi(api_backend,
                            access_token_key=oauth_token,
                            access_token_secret=oauth_token_secret,)

    def start(self):
        self.main_loop()

    def authenticate_api(self):
        self.info_message(_('Authenticating API'))

        self.api.init_api(on_error=self.api_init_error,
                          on_success=self.init_timelines,)

    @async
    def init_timelines(self):
        # API has to be authenticated
        while (not self.api.is_authenticated):
            pass

        # fetch the authenticated user
        self.user = self.api.verify_credentials()

        # initialize the timelines
        self.info_message(_('Initializing timelines'))
        self.append_default_timelines()

        # Main loop has to be running
        while not getattr(self, 'loop'):
            pass

        # update alarm
        seconds = configuration.update_frequency
        self.loop.set_alarm_in(seconds, self.update_alarm)

    def main_loop(self):
        """
        Launch the main loop of the program.
        """
        if not hasattr(self, 'loop'):
            # Creating the main loop for the first time
            self.key_handler = KeyHandler(self)
            handler = self.key_handler.handle
            self.loop = urwid.MainLoop(self.ui,
                                       configuration.palette,
                                       handle_mouse=False,
                                       unhandled_input=handler)

            # Authenticate API just before starting main loop
            self.authenticate_api()

        try:
            self.loop.run()
        except TweepError, message:
            logging.exception(message)
            self.error_message(_('API error: %s' % message))
            # recover from API errors
            self.main_loop()

    def exit(self):
        """Exit the program."""
        raise urwid.ExitMainLoop()

    # -- Observer -------------------------------------------------------------

    def update(self):
        """
        From :class:`~turses.meta.Observer`, gets called when the observed
        subjects change.
        """
        if self.is_in_info_mode():
            self.timeline_mode()
        self.draw_timelines()

    # -- Callbacks ------------------------------------------------------------

    def api_init_error(self):
        # TODO retry
        self.error_message(_('Couldn\'t initialize API'))

    def update_alarm(self, *args, **kwargs):
        self.update_all_timelines()

        seconds = configuration.update_frequency
        self.loop.set_alarm_in(seconds, self.update_alarm)

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self):
        """
        Activates the Timeline mode if there are Timelines.

        If not, shows program info.
        """
        if self.is_in_user_info_mode():
            self.ui.hide_user_info()

        if self.is_in_timeline_mode():
            return

        if self.is_in_help_mode():
            self.clear_status()

        if self.timelines.has_timelines():
            self.mode = self.TIMELINE_MODE
            self.draw_timelines()
        else:
            self.mode = self.INFO_MODE
            self.ui.show_info()

        self.redraw_screen()

    def is_in_timeline_mode(self):
        return self.mode == self.TIMELINE_MODE

    def info_mode(self):
        self.mode = self.INFO_MODE
        self.ui.show_info()
        self.redraw_screen()

    def is_in_info_mode(self):
        return self.mode == self.INFO_MODE

    def help_mode(self):
        """Activate Help mode."""
        if self.is_in_help_mode():
            return

        self.mode = self.HELP_MODE
        self.ui.show_help()
        self.redraw_screen()

    def is_in_help_mode(self):
        return self.mode == self.HELP_MODE

    def editor_mode(self, editor):
        """Activate editor mode."""
        self.editor = editor
        self.mode = self.EDITOR_MODE

    def is_in_editor_mode(self):
        return self.mode == self.EDITOR_MODE

    def user_info_mode(self, user):
        """Activate user info mode."""
        self._user_info = user
        self.mode = self.USER_INFO_MODE

    def is_in_user_info_mode(self):
        return self.mode == self.USER_INFO_MODE

    # -- Timelines ------------------------------------------------------------

    @wrap_exceptions
    def append_timeline(self,
                        name,
                        update_function,
                        update_args=None,
                        update_kwargs=None):
        """
        Given a name, function to update a timeline and optionally
        arguments to the update function, it creates the timeline and
        appends it to `timelines`.
        """
        timeline = Timeline(name=name,
                            update_function=update_function,
                            update_function_args=update_args,
                            update_function_kwargs=update_kwargs)
        timeline.update()
        timeline.activate_first()
        self.timelines.append_timeline(timeline)
        if self.is_in_info_mode():
            #self.timeline_mode()
            pass

    @async
    def append_default_timelines(self):
        timelines = [
            HOME_TIMELINE,
            MENTIONS_TIMELINE,
            FAVORITES_TIMELINE,
            MESSAGES_TIMELINE,
            OWN_TWEETS_TIMELINE,
        ]

        default_timelines = configuration.default_timelines
        is_any_default_timeline = any([default_timelines[timeline] for timeline
                                                                   in timelines])

        if is_any_default_timeline:
            self.timeline_mode()
        else:
            message = _('You don\'t have any default timelines activated')
            self.info_message(message)
            return

        default_timeline_append_functions = {
            HOME_TIMELINE:       self.append_home_timeline,
            MENTIONS_TIMELINE:   self.append_mentions_timeline,
            FAVORITES_TIMELINE:  self.append_favorites_timeline,
            MESSAGES_TIMELINE:   self.append_direct_messages_timeline,
            OWN_TWEETS_TIMELINE: self.append_own_tweets_timeline,
        }

        for timeline in timelines:
            append = default_timeline_append_functions[timeline]
            if default_timelines[timeline]:
                append()

        self.timeline_mode()
        self.clear_status()

    def append_home_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Home timeline fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch home timeline'))

        self.append_timeline(name=_('tweets'),
                             update_function=self.api.get_home_timeline,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_user_timeline(self, username):
        success_message = _('@%s\'s tweets fetched' % username)
        timeline_fetched = partial(self.info_message,
                                   success_message)
        error_message = _('Failed to fetch @%s\'s tweets' % username)
        timeline_not_fetched = partial(self.error_message,
                                       error_message)

        self.append_timeline(name='@%s' % username,
                             update_function=self.api.get_user_timeline,
                             update_kwargs={'screen_name': username},
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_own_tweets_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Your tweets fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch your tweets'))

        if not hasattr(self, 'user'):
            self.user = self.api.verify_credentials()
        self.append_timeline(name='@%s' % self.user.screen_name,
                             update_function=self.api.get_own_timeline,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_mentions_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Mentions fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch mentions'))

        self.append_timeline(name=_('mentions'),
                             update_function=self.api.get_mentions,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_favorites_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Favorites fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch favorites'))

        self.append_timeline(name=_('favorites'),
                             update_function=self.api.get_favorites,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_direct_messages_timeline(self):
        timeline_fetched = partial(self.info_message,
                                    _('Messages fetched'))
        timeline_not_fetched = partial(self.error_message,
                                        _('Failed to fetch messages'))

        self.append_timeline(name=_('messages'),
                             update_function=self.api.get_direct_messages,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched,)

    def append_thread_timeline(self):
        status = self.timelines.active_status

        timeline_fetched = partial(self.info_message,
                                   _('Thread fetched'))
        timeline_not_fetched = partial(self.error_message,
                                       _('Failed to fetch thread'))

        if is_DM(status):
            participants = [status.sender_screen_name,
                            status.recipient_screen_name,]
            name = _('DM thread: %s' % ', '.join(participants))
            update_function = self.api.get_message_thread
        else:
            participants = status.mentioned_usernames
            author = status.authors_username
            if author not in participants:
                participants.insert(0, author)

            name = _('thread: %s' % ', '.join(participants))
            update_function = self.api.get_thread

        self.append_timeline(name=name,
                             update_function=update_function,
                             update_args=status,
                             on_error=timeline_not_fetched,
                             on_success=timeline_fetched)

    @async
    def append_search_timeline(self, query):
        text = query.strip()
        if not is_valid_search_text(text):
            self.error_message(_('Invalid search'))
            return
        else:
            self.info_message(_('Creating search timeline for "%s"' % text))

        success_message = _('Search timeline for "%s" created' % text)
        timeline_created = partial(self.info_message,
                                   success_message)
        error_message = _('Error creating search timeline for "%s"' % text)
        timeline_not_created = partial(self.info_message,
                                       error_message)

        self.append_timeline(name=_('Search: %s' % text),
                             update_function=self.api.search,
                             update_args=text,
                             on_error=timeline_not_created,
                             on_success=timeline_created)

    @async
    def append_retweets_of_me_timeline(self):
        success_message = _('Your retweeted tweet timeline created')
        timeline_created = partial(self.info_message,
                                   success_message)
        error_message = _('Error creating timeline for your retweeted tweets')
        timeline_not_created = partial(self.info_message,
                                       error_message)

        self.append_timeline(name=_('Retweets of %s' % self.user.screen_name),
                             update_function=self.api.get_retweets_of_me,
                             on_error=timeline_not_created,
                             on_success=timeline_created)

    @async
    def update_all_timelines(self):
        for timeline in self.timelines:
            timeline.update()
            self.draw_timelines()
            self.info_message(_('%s updated' % timeline.name))
        self.clear_status()

    # -- Timeline mode --------------------------------------------------------

    def draw_timelines(self):
        if not self.is_in_timeline_mode():
            return

        if self.timelines.has_timelines():
            self.update_header()

            # draw visible timelines
            visible_timelines = self.timelines.visible_timelines
            self.ui.draw_timelines(visible_timelines)

            # focus active timeline
            active_timeline = self.timelines.active
            active_pos = self.timelines.active_index_relative_to_visible

            # focus active status (if any)
            if active_timeline.active_index >= 0:
                self.ui.focus_timeline(active_pos)
                self.ui.focus_status(active_timeline.active_index)
        else:
            self.ui.clear_header()

    def update_header(self):
        template = configuration.styles['tab_template']
        name_and_unread = [(tl.name, tl.unread_count) for tl in self.timelines]

        tabs = [template.format(timeline_name=name, unread=unread)
                for (name, unread) in name_and_unread]
        self.ui.set_tab_names(tabs)

        # highlight the active
        active_index = self.timelines.active_index
        self.ui.activate_tab(active_index)

        # colorize the visible tabs
        visible_indexes = self.timelines.visible
        self.ui.highlight_tabs(visible_indexes)

    def mark_all_as_read(self):
        """Mark all statuses in active timeline as read."""
        active_timeline = self.timelines.active
        for tweet in active_timeline:
            tweet.read = True
        self.update_header()

    @async
    def update_active_timeline(self):
        """Update the active timeline and draw the timeline buffers."""
        if self.timelines.has_timelines():
            active_timeline = self.timelines.active
            try:
                newest = active_timeline[0]
            except IndexError:
                return
            active_timeline.update(since_id=newest.id)
            if self.is_in_timeline_mode():
                self.draw_timelines()
            self.info_message('%s updated' % active_timeline.name)

    @async
    def update_active_timeline_with_newer_statuses(self):
        """
        Updates the active timeline with newer tweets than the active.
        """
        active_timeline = self.timelines.active
        active_status = active_timeline.active
        if active_status:
            active_timeline.update(since_id=active_status.id)

    @async
    def update_active_timeline_with_older_statuses(self):
        """
        Updates the active timeline with older tweets than the active.
        """
        active_timeline = self.timelines.active
        active_status = active_timeline.active
        if active_status:
            active_timeline.update(max_id=active_status.id)

        # Center focus in order to make the fetched tweets visible
        self.draw_timelines()
        self.ui.center_focus()
        self.redraw_screen()

    @has_timelines
    def previous_timeline(self):
        self.timelines.activate_previous()

    @has_timelines
    def next_timeline(self):
        self.timelines.activate_next()

    @has_timelines
    def shift_buffer_left(self):
        self.timelines.shift_active_previous()

    @has_timelines
    def shift_buffer_right(self):
        self.timelines.shift_active_next()

    @has_timelines
    def shift_buffer_beggining(self):
        self.timelines.shift_active_beggining()

    @has_timelines
    def shift_buffer_end(self):
        self.timelines.shift_active_end()

    @has_timelines
    def expand_buffer_left(self):
        self.timelines.expand_visible_previous()

    @has_timelines
    def expand_buffer_right(self):
        self.timelines.expand_visible_next()

    @has_timelines
    def shrink_buffer_left(self):
        self.timelines.shrink_visible_beggining()

    @has_timelines
    def shrink_buffer_right(self):
        self.timelines.shrink_visible_end()

    @has_timelines
    def activate_first_buffer(self):
        self.timelines.activate_first()

    @has_timelines
    def activate_last_buffer(self):
        self.timelines.activate_last()

    def delete_buffer(self):
        self.timelines.delete_active_timeline()
        if not self.timelines.has_timelines():
            self.info_mode()

    # -- Motion ---------------------------------------------------------------

    def scroll_up(self):
        self.ui.focus_previous()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            # update with newer tweets when scrolling down being at the bottom
            if active_timeline.active_index == 0:
                self.update_active_timeline_with_newer_statuses()
            active_timeline.activate_previous()
            self.draw_timelines()

    def scroll_down(self):
        self.ui.focus_next()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            # update with older tweets when scrolling down being at the bottom
            if active_timeline.active_index == len(active_timeline) - 1:
                self.update_active_timeline_with_older_statuses()
            active_timeline.activate_next()
            self.draw_timelines()

    def scroll_top(self):
        self.ui.focus_first()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            active_timeline.activate_first()
            self.draw_timelines()

    def scroll_bottom(self):
        self.ui.focus_last()
        if self.is_in_timeline_mode():
            active_timeline = self.timelines.active
            active_timeline.activate_last()
            self.draw_timelines()

    # -- Footer ---------------------------------------------------------------

    def error_message(self, message):
        self.ui.status_error_message(message)
        self.redraw_screen()

    def info_message(self, message):
        self.ui.status_info_message(message)
        self.redraw_screen()

    def clear_status(self):
        """Clear the status bar."""
        self.ui.clear_status()
        self.redraw_screen()

    # -- UI -------------------------------------------------------------------
    def redraw_screen(self):
        if hasattr(self, "loop"):
            try:
                self.loop.draw_screen()
            except AssertionError, message:
                logging.critical(message)

    # -- Editor ---------------------------------------------------------------

    def forward_to_editor(self, key):
        if self.editor:
            # FIXME: `keypress` function needs a `size` parameter
            size = 20,
            self.editor.keypress(size, key)

    @text_from_editor
    def tweet_handler(self, text):
        """Handle the post as a tweet of the given `text`."""
        self.info_message(_('Sending tweet'))

        if not is_valid_status_text(text):
            # tweet was explicitly cancelled or empty text
            self.info_message(_('Tweet canceled'))
            return

        tweet_sent = partial(self.info_message, _('Tweet sent'))
        tweet_not_sent = partial(self.error_message, _('Tweet not sent'))

        # API call
        self.api.update(text=text,
                        on_success=tweet_sent,
                        on_error=tweet_not_sent,)

    @text_from_editor
    def direct_message_handler(self, username, text):
        """Handle the post as a DM of the given `text` to `username`."""
        self.info_message(_('Sending DM'))

        if not is_valid_status_text(text):
            # <Esc> was pressed
            self.info_message(_('DM canceled'))
            return

        dm_info = _('Direct Message to @%s sent' % username)
        dm_sent = partial(self.info_message, dm_info)
        dm_error = _('Failed to send message to @%s' % username)
        dm_not_sent = partial(self.error_message, dm_error)

        self.api.direct_message(screen_name=username,
                                text=text,
                                on_success=dm_sent,
                                on_error=dm_not_sent,)

    @text_from_editor
    def follow_user_handler(self, username):
        """
        Handles following the user given in `username`.
        """
        if username is None:
            self.info_message(_('Search cancelled'))
            return

        username = sanitize_username(username)
        if username == self.user.screen_name:
            self.error_message(_('You can\'t follow yourself'))
            return

        # TODO make sure that the user EXISTS and THEN follow
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Following @%s' % username))

        success_message = _('You are now following @%s' % username)
        follow_done = partial(self.info_message,
                              success_message)

        error_template = _('We can not ensure that you are following @%s')
        error_message = error_template % username
        follow_error = partial(self.error_message,
                               error_message)

        self.api.create_friendship(screen_name=username,
                                   on_error=follow_error,
                                   on_success=follow_done)

    @text_from_editor
    def unfollow_user_handler(self, username):
        """
        Handles unfollowing the user given in `username`.
        """
        if username is None:
            self.info_message(_('Search cancelled'))
            return

        username = sanitize_username(username)
        if username == self.user.screen_name:
            self.error_message(_('That doesn\'t make any sense'))
            return

        # TODO make sure that the user EXISTS and THEN follow
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Unfollowing @%s' % username))

        success_message = _('You are no longer following %s' % username)
        unfollow_done = partial(self.info_message,
                                success_message)

        error_template = _('We can not ensure that you are not following %s')
        error_message = error_template % username
        unfollow_error = partial(self.error_message,
                                 error_message)

        self.api.destroy_friendship(screen_name=username,
                                    on_error=unfollow_error,
                                    on_success=unfollow_done)

    @text_from_editor
    def search_handler(self, text):
        """
        Handles creating a timeline tracking the search term given in
        `text`.
        """
        if text is None:
            self.info_message(_('Search cancelled'))
            return
        self.append_search_timeline(text)

    @text_from_editor
    def search_user_handler(self, username):
        """
        Handles creating a timeline tracking the searched user's tweets.
        """
        if username is None:
            self.info_message(_('Search cancelled'))
            return

        # TODO make sure that the user EXISTS and THEN fetch its tweets
        username = sanitize_username(username)
        if not is_username(username):
            self.info_message(_('Invalid username'))
            return
        else:
            self.info_message(_('Fetching latest tweets from @%s' % username))

        success_message = _('@%s\'s timeline created' % username)
        timeline_created = partial(self.info_message,
                                   success_message)
        error_message = _('Unable to create @%s\'s timeline' % username)
        timeline_not_created = partial(self.error_message,
                                       error_message)

        self.append_timeline(name='@%s' % username,
                             update_function=self.api.get_user_timeline,
                             update_args=username,
                             on_success=timeline_created,
                             on_error=timeline_not_created)

    # -- Twitter --------------------------------------------------------------

    def search(self, text=None):
        text = '' if text is None else text
        handler = self.search_handler
        editor = self.ui.show_text_editor(prompt='Search',
                                          content=text,
                                          done_signal_handler=handler)
        self.editor_mode(editor)

    def search_user(self):
        prompt = _('Search user (no need to prepend it with "@"')
        handler = self.search_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                 content='',
                                 done_signal_handler=handler)
        self.editor_mode(editor)

    @has_active_status
    def search_hashtags(self):
        status = self.timelines.active_status

        hashtags = ' '.join(status.hashtags)
        self.search_handler(text=hashtags)

    @has_active_status
    def focused_status_author_timeline(self):
        status = self.timelines.active_status

        author = status.authors_username
        self.append_user_timeline(author)

    def tweet(self,
              prompt=_('Tweet'),
              content='',
              cursor_position=None):
        handler = self.tweet_handler
        editor = self.ui.show_tweet_editor(prompt=prompt,
                                           content=content,
                                           done_signal_handler=handler,
                                           cursor_position=cursor_position)
        self.editor_mode(editor)

    @has_active_status
    def retweet(self):
        status = self.timelines.active_status

        if is_DM(status):
            self.error_message(_('You can\'t retweet direct messages'))
            return

        retweet_posted = partial(self.info_message,
                                 _('Retweet posted'))
        retweet_post_failed = partial(self.error_message,
                                      _('Failed to post retweet'))
        self.api.retweet(on_error=retweet_post_failed,
                         on_success=retweet_posted,
                         status=status,)

    @has_active_status
    def manual_retweet(self):
        status = self.timelines.active_status

        rt_text = ''.join([' RT @%s: ' % status.authors_username,
                           status.text])
        if is_valid_status_text(rt_text):
            self.tweet(content=rt_text,
                       cursor_position=0)
        else:
            self.error_message(_('Tweet too long for manual retweet'))

    # TODO: add `in_reply_to_status_id` parameter
    @has_active_status
    def reply(self):
        status = self.timelines.active_status

        if is_DM(status):
            self.direct_message()
            return

        author = status.authors_username
        mentioned = status.mentioned_for_reply
        try:
            mentioned.remove('@%s' % self.user.screen_name)
        except ValueError:
            pass

        handler = self.tweet_handler
        editor = self.ui.show_tweet_editor(prompt=_('Reply to %s' % author),
                                           content=' '.join(mentioned),
                                           done_signal_handler=handler)
        self.editor_mode(editor)

    @has_active_status
    def direct_message(self):
        status = self.timelines.active_status

        recipient = status.dm_recipients_username(self.user.screen_name)
        if recipient:
            handler = self.direct_message_handler
            editor = self.ui.show_dm_editor(prompt=_('DM to %s' % recipient),
                                            content='',
                                            recipient=recipient,
                                            done_signal_handler=handler)
            self.editor_mode(editor)
        else:
            self.error_message(_('What do you mean?'))

    @has_active_status
    def tweet_with_hashtags(self):
        status = self.timelines.active_status

        hashtags = ' '.join(status.hashtags)
        if hashtags:
            handler = self.tweet_handler
            content = ''.join([' ', hashtags])
            editor = self.ui.show_tweet_editor(prompt=_('%s' % hashtags),
                                               content=content,
                                               done_signal_handler=handler,
                                               cursor_position=0)
            self.editor_mode(editor)

    @has_active_status
    def delete_tweet(self):
        status = self.timelines.active_status

        if is_DM(status):
            self.delete_dm()
            return

        author = status.authors_username
        if (author != self.user.screen_name and
            status.user != self.user.screen_name):
            self.error_message(_('You can only delete your own tweets'))
            return

        status_deleted = partial(self.info_message,
                                 _('Tweet deleted'))
        status_not_deleted = partial(self.error_message,
                                     _('Failed to delete tweet'))

        self.api.destroy_status(status=status,
                                on_error=status_not_deleted,
                                on_success=status_deleted)

    def delete_dm(self):
        dm = self.timelines.active_status
        if dm is None:
            return

        if dm.sender_screen_name != self.user.screen_name:
            self.error_message(_('You can only delete messages sent by you'))
            return

        dm_deleted = partial(self.info_message,
                             _('Message deleted'))
        dm_not_deleted = partial(self.error_message,
                                 _('Failed to delete message'))

        self.api.destroy_direct_message(status=dm,
                                        on_error=dm_not_deleted,
                                        on_success=dm_deleted)

    @has_active_status
    def follow_selected(self):
        status = self.timelines.active_status

        username = status.authors_username
        if username == self.user.screen_name:
            self.error_message(_('You can\'t follow yourself'))
            return

        success_message = _('You are now following @%s' % username)
        follow_done = partial(self.info_message,
                              success_message)

        error_template = _('We can not ensure that you are following @%s')
        error_message = error_template % username
        follow_error = partial(self.error_message,
                               error_message)

        self.api.create_friendship(screen_name=username,
                                   on_error=follow_error,
                                   on_success=follow_done)

    def follow_user(self,
                    prompt=_('Follow user (no need to prepend it with "@"'),
                    content='',
                    cursor_position=None):
        handler = self.follow_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                          content=content,
                                          done_signal_handler=handler,
                                          cursor_position=cursor_position)
        self.editor_mode(editor)

    def unfollow_user(self,
                      prompt=_('Unfollow user (no need to prepend it with'
                               ' "@"'),
                      content='',
                      cursor_position=None):
        handler = self.unfollow_user_handler
        editor = self.ui.show_text_editor(prompt=prompt,
                                          content=content,
                                          done_signal_handler=handler,
                                          cursor_position=cursor_position)
        self.editor_mode(editor)

    @has_active_status
    def unfollow_selected(self):
        status = self.timelines.active_status

        username = status.authors_username
        if username == self.user.screen_name:
            self.error_message(_('That doesn\'t make any sense'))
            return

        success_message = _('You are no longer following %s' % username)
        unfollow_done = partial(self.info_message,
                                success_message)

        error_template = _('We can not ensure that you are not following %s')
        error_message = error_template % username
        unfollow_error = partial(self.error_message,
                                 error_message)

        self.api.destroy_friendship(screen_name=username,
                                    on_error=unfollow_error,
                                    on_success=unfollow_done)

    @has_active_status
    def favorite(self):
        status = self.timelines.active_status

        favorite_error = partial(self.error_message,
                                 _('Failed to mark tweet as favorite'))
        favorite_done = partial(self.info_message,
                                _('Tweet marked as favorite'))
        self.api.create_favorite(on_error=favorite_error,
                                 on_success=favorite_done,
                                 status=status,)

    @has_active_status
    def unfavorite(self):
        status = self.timelines.active_status

        unfavorite_error = partial(self.error_message,
                                   _('Failed to remove tweet from favorites'))
        unfavorite_done = partial(self.info_message,
                                  _('Tweet removed from favorites'))
        self.api.destroy_favorite(on_error=unfavorite_error,
                                  on_success=unfavorite_done,
                                  status=status,)

    @has_active_status
    def user_info(self):
        status = self.timelines.active_status

        user = self.api.get_user(status.authors_username)
        self.ui.show_user_info(user)
        self.user_info_mode(user)

    # - Configuration ---------------------------------------------------------

    def reload_configuration(self):
        configuration.reload()
        self.redraw_screen()
        self.info_message(_('Configuration reloaded'))

    # - Browser ---------------------------------------------------------------

    @has_active_status
    def open_urls(self):
        """
        Open the URLs contained on the focused tweets in a browser.
        """
        status = self.timelines.active_status
        urls = get_urls(status.text)

        if not urls:
            self.info_message(_('No URLs found on this tweet'))
            return

        self.open_urls_in_browser(urls)

    @has_active_status
    def open_status_url(self):
        """
        Open the focused tweet in a browser.
        """
        status = self.timelines.active_status

        if is_DM(status):
            message = _('You only can open regular statuses in a browser')
            self.info_message(message)
            return

        self.open_urls_in_browser([status.url])

    def open_urls_in_browser(self, urls):
        """
        Open `urls` in $BROWSER if the environment variable is set.
        """
        # The webbrowser module respects the BROWSER environment variable,
        # so if that's set, it'll use it, otherwise it will try to find
        # something sensible
        try:
            # Firefox, w3m, etc can't handle multiple URLs at command line, so
            # split the URLs up for them
            for url in urls:
                webbrowser.open(url)
        except Exception, message:
            logging.exception(message)
            self.error_message(_('Unable to launch the browser'))
