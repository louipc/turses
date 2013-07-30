"""
This module contains various methods for checking the type of timelines and a
class that creates all kinds of timelines.
"""

import re
from functools import partial
from gettext import gettext as _

from turses.models import Timeline, is_DM


HOME_TIMELINE = 'home'
MENTIONS_TIMELINE = 'mentions'
FAVORITES_TIMELINE = 'favorites'
MESSAGES_TIMELINE = 'messages'
OWN_TWEETS_TIMELINE = 'own_tweets'

DEFAULT_TIMELINES = [
    HOME_TIMELINE,
    MENTIONS_TIMELINE,
    FAVORITES_TIMELINE,
    MESSAGES_TIMELINE,
    OWN_TWEETS_TIMELINE,
]


def check_update_function_name(timeline, update_function_name=None):
    if not isinstance(timeline, Timeline):
        return False

    update_function = timeline.update_function
    if update_function is None:
        return False

    return update_function.__name__ == update_function_name

is_home_timeline = partial(check_update_function_name,
                           update_function_name='get_home_timeline')
is_mentions_timeline = partial(check_update_function_name,
                               update_function_name='get_mentions')
is_favorites_timeline = partial(check_update_function_name,
                                update_function_name='get_favorites')
is_own_timeline = partial(check_update_function_name,
                          update_function_name='get_own_timeline')
is_messages_timeline = partial(check_update_function_name,
                               update_function_name='get_direct_messages')
is_search_timeline = partial(check_update_function_name,
                             update_function_name='search')
is_user_timeline = partial(check_update_function_name,
                           update_function_name='get_user_timeline')
is_retweets_of_me_timeline = partial(check_update_function_name,
                                     update_function_name='get_retweets_of_me')
is_thread_timeline = partial(check_update_function_name,
                             update_function_name='get_thread')


search_name_re = re.compile(r'^search:(?P<query>.+)$')
hashtag_name_re = re.compile(r'^hashtag:(?P<query>.+)$')
user_name_re = re.compile(r'^user:(?P<screen_name>[A-Za-z0-9_]+)$')


class TimelineFactory:
    def __init__(self, api):
        self.api = api

    def __call__(self, timeline_string):
        timeline = timeline_string.strip()

        if timeline == HOME_TIMELINE:
            return Timeline(name=_('tweets'),
                            update_function=self.api.get_home_timeline,)
        elif timeline == MENTIONS_TIMELINE:
            return Timeline(name=_('mentions'),
                            update_function=self.api.get_mentions,)
        elif timeline == FAVORITES_TIMELINE:
            return Timeline(name=_('favorites'),
                            update_function=self.api.get_favorites,)
        elif timeline == MESSAGES_TIMELINE:
            return Timeline(name=_('messages'),
                            update_function=self.api.get_direct_messages,)
        elif timeline == OWN_TWEETS_TIMELINE:
            return Timeline(name=_('me'),
                            update_function=self.api.get_own_timeline,)
        elif timeline == 'retweets_of_me':
            return Timeline(name=_('retweets of me'),
                            update_function=self.api.get_retweets_of_me,)

        is_search = search_name_re.match(timeline)
        if is_search:
            query = is_search.groupdict()['query']
            return Timeline(name=_('Search: %s' % query),
                            update_function=self.api.search,
                            update_function_args=query,)

        is_hashtag = hashtag_name_re.match(timeline)
        if is_hashtag:
            query = "#{}".format(is_hashtag.groupdict()['query'])
            return Timeline(name=_('hashtag: %s' % query),
                            update_function=self.api.search,
                            update_function_args=query,)

        is_user = user_name_re.match(timeline)
        if is_user:
            screen_name = is_user.groupdict()['screen_name']
            timeline_name = _('@{screen_name}'.format(screen_name=screen_name))
            return Timeline(name=timeline_name,
                            update_function=self.api.get_user_timeline,
                            update_function_args=screen_name,)

    def valid_timeline_name(self, name):
        if name in DEFAULT_TIMELINES:
            return True

        if name == 'retweets_of_me':
            return True

        # search
        if search_name_re.match(name):
            return True

        # user
        if user_name_re.match(name):
            return True

        return False

    def thread(self, status):
        """
        Create a timeline with the conversation to which `status` belongs.
        `status` can be a regular status or a direct message.
        """
        if is_DM(status):
            participants = [status.sender_screen_name,
                            status.recipient_screen_name]
            name = _('DM thread: %s' % ', '.join(participants))
            update_function = self.api.get_message_thread
        else:
            participants = status.mentioned_usernames
            author = status.authors_username
            if author not in participants:
                participants.insert(0, author)

            name = _('thread: %s' % ', '.join(participants))
            update_function = self.api.get_thread

        return Timeline(name=name,
                        update_function=update_function,
                        update_function_args=status,)
