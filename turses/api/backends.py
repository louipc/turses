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

from turses.models import User, Status, DirectMessage
from turses.api.base import ApiAdapter


def include_entities(func):
    """
    Injects the `include_entities=True` keyword argument into `func`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        kwargs.update({'include_entities': True})
        return func(*args, **kwargs)
    return wrapper

# Decorators for converting data to `turses.models`

def filter_result(func, filter_func=None):
    """
    Decorator for filtering the output of `func` with `filter_func`.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)

        if isinstance(result, list):
            return [filter_func(elem) for elem in result]
        else:
            return filter_func(result)
    return wrapper


def _to_status(status, **extra_kwargs):
    """
    Convert a `tweepy.Status` to a `turses.models.Status`.
    """
    text = status.text

    is_reply = False
    in_reply_to_user = ''
    is_retweet = False
    retweet_count = 0
    retweeted_status = None
    is_favorite = False
    author = ''

    # When fetching an individual user her last status is included and
    # does not include a `user` attribute
    if getattr(status, 'user', None):
        user = status.user.screen_name
    else:
        user = None

    if hasattr(status, 'retweeted_status'):
        is_retweet = True
        retweeted_status = _to_status(status.retweeted_status)
        retweet_count = status.retweet_count

        # the `retweeted_status` could not have a `user` attribute
        # (e.g. when fetching a user and her last status is a retweet)
        if hasattr(status.retweeted_status, 'user'):
            author = status.retweeted_status.user.screen_name

    if hasattr(status, 'in_reply_to_screen_name'):
        is_reply = True
        in_reply_to_user = status.in_reply_to_screen_name

    if hasattr(status, 'favorited'):
        is_favorite = status.favorited

    kwargs = {
        'id': status.id,
        'created_at': status.created_at,
        'user': user,
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
    kwargs.update(**extra_kwargs)

    return Status(**kwargs)


def _to_status_from_search_result(status):
    """
    Convert a `tweepy.SearchResult` to a `turses.models.Status`.
    """
    kwargs = {
        'id': status.id,
        'created_at': status.created_at,
        'user': status.from_user,
        'text': status.text,
        'entities': getattr(status, 'entities', None),
    }
    return Status(**kwargs)


def _to_direct_message(dm):
    """
    Convert a `tweepy.DirectMessage` to a `turses.models.DirectMessage`.
    """
    kwargs = {
        'id': dm.id,
        'created_at': dm.created_at,
        'sender_screen_name': dm.sender_screen_name,
        'recipient_screen_name': dm.recipient_screen_name,
        'text': dm.text,
        'entities': getattr(dm, 'entities', None),
    }
    return DirectMessage(**kwargs)


def _to_user(user):
    """
    Convert a `tweepy.User` to a `turses.models.User`.
    """
    kwargs = {
        'id': user.id,
        'name': user.name,
        'screen_name': user.screen_name,
        'description': user.description,
        'url': user.url,
        'created_at': user.created_at,
        'friends_count': user.friends_count,
        'followers_count': user.followers_count,
        'favorites_count': user.favourites_count,
        'status': _to_status(user.status, user=user.screen_name),
    }
    return User(**kwargs)

to_status = partial(filter_result,
                    filter_func=_to_status)
to_status_from_search_result = partial(filter_result,
                                       filter_func=_to_status_from_search_result)
to_direct_message = partial(filter_result,
                            filter_func=_to_direct_message)
to_user = partial(filter_result,
                  filter_func=_to_user)


class TweepyApi(BaseTweepyApi, ApiAdapter):
    """
    A `ApiAdapter` implementation using `tweepy` library.

        http://github.com/tweepy/tweepy/
    """

    def __init__(self, *args, **kwargs):
        ApiAdapter.__init__(self, *args, **kwargs)

    # from `turses.api.base.ApiAdapter`

    def init_api(self):
        oauth_handler = TweepyOAuthHandler(self._consumer_key,
                                           self._consumer_secret)
        oauth_handler.set_access_token(self._access_token_key,
                                       self._access_token_secret)
        self._api = BaseTweepyApi(oauth_handler)

    @to_user
    def verify_credentials(self):
        return self._api.me()

    @to_user
    @include_entities
    def get_user(self, screen_name, **kwargs):
        return self._api.get_user(screen_name=screen_name, **kwargs)

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

    # NOTE:
    #  `get_thread` is not decorated with `to_status` because
    #  it uses `TweepyApi.get_user_timeline` which is already
    #  decorated
    @include_entities
    def get_thread(self, status, **kwargs):
        """
        Get the conversation to which `status` belongs.

        It filters the last tweets by the participanting users and
        based on mentions to each other.
        """
        author = status.authors_username
        mentioned = status.mentioned_usernames
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

    @to_status_from_search_result
    @include_entities
    def search(self, text, **kwargs):
        return self._api.search(text, **kwargs)

    def update(self, text):
        self._api.update_status(text)

    def destroy_status(self, status):
        self._api.destroy_status(status.id)

    def retweet(self, status):
        self._api.retweet(status.id)

    def direct_message(self, username, text):
        self._api.send_direct_message(user=username, text=text)

    def destroy_direct_message(self, dm):
        self._api.destroy_direct_message(dm.id)

    def create_friendship(self, screen_name):
        self._api.create_friendship(screen_name=screen_name)

    def destroy_friendship(self, screen_name):
        self._api.destroy_friendship(screen_name=screen_name)

    def create_favorite(self, status):
        self._api.create_favorite(status.id)

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
