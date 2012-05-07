# -*- coding: utf-8 -*-

"""
turses.api.backends
~~~~~~~~~~~~~~~~~~~

This module contains implementations of `turses.api.base.Api` using multiple
API backends.
"""

from functools import wraps, partial

from tweepy import API as BaseTweepyApi
from tweepy import OAuthHandler as TweepyOAuthHandler

from turses.models import (User, Status, DirectMessage, 
                           get_authors_username, get_mentioned_usernames)
from turses.api.base import Api, include_entities


# Decorators for converting data to `turses.models`

def filter_with(func, filter_func=None):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, list):
            return [filter_func(elem) for elem in result]
        else:
            return filter_func(result)
    return wrapper

def _to_status(status):
    text = status.text

    is_reply = False
    in_reply_to_user = ''
    is_retweet = False
    retweet_count = 0
    retweeted_status = None
    is_favorite = False
    author = ''

    if getattr(status, 'retweeted_status', False):
        is_retweet = True
        retweeted_status = _to_status(status.retweeted_status)
        retweet_count = status.retweet_count
        author = status.retweeted_status.author.screen_name

    if status.in_reply_to_screen_name:
        is_reply = True
        in_reply_to_user = status.in_reply_to_screen_name

    if status.favorited:
        is_favorite = True

    kwargs = {
        'id': status.id,
        'created_at': status.created_at,
        'user': status.user.screen_name,
        'text': text,
        'is_retweet': is_retweet,
        'is_reply': is_reply,
        'is_favorite': is_favorite,
        'in_reply_to_user': in_reply_to_user,
        'retweet_count': retweet_count,
        'retweeted_status': retweeted_status,
        'author': author,
        'entities': getattr(status, 'entities', None),
    }
    return Status(**kwargs)

def _to_direct_message(dm):
    kwargs = {
        'id': dm.id,
        'created_at': dm.created_at,
        'sender_screen_name': dm.sender_screen_name,
        'recipient_screen_name': dm.recipient_screen_name,
        'text': dm.text,
        'entities': getattr(dm, 'entities', None),
    }
    return DirectMessage(**kwargs)

to_status = partial(filter_with, filter_func=_to_status)
to_direct_message = partial(filter_with, filter_func=_to_direct_message)


class TweepyApi(BaseTweepyApi, Api):
    """
    A `Api` implementation using `tweepy` library.

        http://github.com/tweepy/tweepy/
    """

    def __init__(self, *args, **kwargs):
        Api.__init__(self, *args, **kwargs)

    # from `turses.api.base.Api`

    def init_api(self):
        oauth_handler = TweepyOAuthHandler(self._consumer_key,
                                           self._consumer_secret)
        oauth_handler.set_access_token(self._access_token_key,
                                       self._access_token_secret)
        self._api = BaseTweepyApi(oauth_handler)

    def verify_credentials(self):
        def to_user(user):
            kwargs = {
                'screen_name': user.screen_name,
            }
            return User(**kwargs)
        return to_user(self._api.me())

    # timelines

    @to_status
    @include_entities
    def get_home_timeline(self, **kwargs):
        tweets = self._api.home_timeline(**kwargs)
        retweets = self._api.retweeted_to_me(**kwargs)
        tweets.extend(retweets)
        return tweets

    @to_status
    @include_entities
    def get_user_timeline(self, screen_name, **kwargs):
        return self._api.user_timeline(screen_name, **kwargs)

    @to_status
    @include_entities
    def get_own_timeline(self, **kwargs):
        me = self.verify_credentials()
        tweets = self._api.user_timeline(screen_name=me.screen_name,
                                         **kwargs)
        retweets = self._api.retweeted_by_me(**kwargs)
        tweets.extend(retweets)
        return tweets

    @to_status
    @include_entities
    def get_mentions(self, **kwargs):
        return self._api.mentions(**kwargs)

    @to_status
    @include_entities
    def get_favorites(self, **kwargs):
        return self._api.favorites(**kwargs)

    @to_direct_message
    @include_entities
    def get_direct_messages(self, **kwargs):
        dms = self._api.direct_messages(**kwargs)
        sent = self._api.sent_direct_messages(**kwargs)
        dms.extend(sent)
        return dms

    @include_entities
    def get_thread(self, status, **kwargs):
        """
        Get the conversation to which `status` belongs.

        It filters the last tweets by the participanting users and
        based on mentions to each other.
        """
        # NOTE:
        #  `get_thread` is not decorated with `to_status` because
        #  it uses `TweepyApi.get_user_timeline` which is already
        #  decorated
        author = get_authors_username(status)
        mentioned = get_mentioned_usernames(status)
        if author not in mentioned:
            mentioned.append(author)

        tweets = []
        for username in mentioned:
            tweets.extend(self.get_user_timeline(username, **kwargs))

        def belongs_to_conversation(status):
            for username in mentioned:
                if username in status.text:
                    return True

        return filter(belongs_to_conversation, tweets)

    @include_entities
    def get_search(self, text, **kwargs):
        # `tweepy.API.search` returns `tweepy.models.SearchResult` objects instead
        # `tweepy.models.Status` so we have to convert them differently
        def to_status(status):
            kwargs = {
                'id': status.id,
                'created_at': status.created_at,
                'user': status.from_user,
                'text': status.text,
            }
            return Status(**kwargs)

        results = self._api.search(text, **kwargs)
        return [to_status(result) for result in results]

    def update(self, text):
        return self._api.update_status(text)

    @to_status
    def destroy_status(self, status):
        return self._api.destroy_status(status.id)

    @to_status
    def retweet(self, status):
        return self._api.retweet(status.id)

    @to_direct_message
    def direct_message(self, username, text):
        return self._api.send_direct_message(user=username, text=text)

    @to_direct_message
    def destroy_direct_message(self, dm):
        return self._api.destroy_direct_message(dm.id)

    # TODO: convert to `turses.models.User`
    def create_friendship(self, screen_name):
        self._api.create_friendship(screen_name=screen_name)

    def destroy_friendship(self, screen_name):
        self._api.destroy_friendship(screen_name=screen_name)

    @to_status
    def create_favorite(self, status):
        self._api.create_favorite(status.id)

    @to_status
    def destroy_favorite(self, status):
        self._api.destroy_favorite(status.id)

    # list methods

    def get_lists(self, screen_name):
        raise NotImplementedError

    def get_own_lists(self):
        raise NotImplementedError

    def get_list_memberships(self):
        raise NotImplementedError

    def get_list_subscriptions(self):
        raise NotImplementedError

    def get_list_timeline(self, list):
        raise NotImplementedError

    def get_list_members(self, list):
        raise NotImplementedError

    def is_list_member(self, user, list):
        raise NotImplementedError

    def subscribe_to_list(self, list):
        raise NotImplementedError

    def get_list_subscribers(self, list):
        raise NotImplementedError

    def is_list_subscriber(self, user, list):
        raise NotImplementedError
