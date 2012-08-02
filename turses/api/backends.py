# -*- coding: utf-8 -*-

"""
This module contains implementations of `turses.api.base.Api` using multiple
API backends.
"""

from functools import wraps, partial

from tweepy import API as BaseTweepyApi
from tweepy import OAuthHandler as TweepyOAuthHandler

from turses.meta import filter_result
from turses.models import User, Status, DirectMessage, List
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


def _to_status(status, **kwargs):
    """
    Convert a `tweepy.Status` to a `turses.models.Status`.
    """
    defaults = {
        'id': status.id,
        'created_at': status.created_at,
        'user': None,
        'text': status.text,
        'is_reply': False,
        'is_retweet': False,
        'is_favorite': False,
        'in_reply_to_user': '',
        'retweeted_status': None,
        'retweet_count': 0,
        'author': '',
        'entities': getattr(status, 'entities', None),
    }

    # When fetching an individual user her last status is included and
    # does not include a `user` attribute
    if getattr(status, 'user', None):
        defaults['user'] = status.user.screen_name

    if hasattr(status, 'retweeted_status'):
        defaults['is_retweet'] = True
        defaults['retweeted_status'] = _to_status(status.retweeted_status)
        defaults['retweet_count'] = status.retweet_count

        # the `retweeted_status` could not have a `user` attribute
        # (e.g. when fetching a user and her last status is a retweet)
        if hasattr(status.retweeted_status, 'user'):
            defaults['author'] = status.retweeted_status.user.screen_name

    if getattr(status, 'in_reply_to_screen_name', False):
        defaults['is_reply'] = True
        defaults['in_reply_to_user'] = status.in_reply_to_screen_name

    if hasattr(status, 'favorited'):
        defaults['is_favorite'] = status.favorited

    defaults.update(**kwargs)
    return Status(**defaults)


def _to_status_from_search(status, **kwargs):
    """
    Convert a `tweepy.SearchResult` to a `turses.models.Status`.
    """
    defaults = {
        'id': status.id,
        'created_at': status.created_at,
        'user': status.from_user,
        'text': status.text,
        'entities': getattr(status, 'entities', None),
    }

    defaults.update(**kwargs)
    return Status(**defaults)


def _to_direct_message(dm, **kwargs):
    """
    Convert a `tweepy.DirectMessage` to a `turses.models.DirectMessage`.
    """
    defaults = {
        'id': dm.id,
        'created_at': dm.created_at,
        'sender_screen_name': dm.sender_screen_name,
        'recipient_screen_name': dm.recipient_screen_name,
        'text': dm.text,
        'entities': getattr(dm, 'entities', None),
    }

    defaults.update(**kwargs)
    return DirectMessage(**defaults)


def _to_user(user, **kwargs):
    """
    Convert a `tweepy.User` to a `turses.models.User`.
    """

    defaults = {
        'id': user.id,
        'name': user.name,
        'screen_name': user.screen_name,
        'description': user.description,
        'url': user.url,
        'created_at': user.created_at,
        'friends_count': user.friends_count,
        'followers_count': user.followers_count,
        'favorites_count': user.favourites_count,
    }

    if hasattr(user, 'status'):
        status = _to_status(user.status, user=user.screen_name)
        defaults['status'] = status

    defaults.update(**kwargs)
    return User(**defaults)


def _to_list(a_list, **kwargs):
    """
    Convert a `tweepy.List` to a `turses.models.List`.
    """
    defaults = {
        'id': a_list.id,
        'owner': _to_user(a_list.user),
        # TODO: `created_at` should be a datetime object
        'created_at': a_list.created_at,
        'name': a_list.name,
        'slug': a_list.slug,
        'description': a_list.description,
        'member_count': a_list.member_count,
        'subscriber_count': a_list.subscriber_count,
        'private': a_list.mode == u'private',
    }

    defaults.update(**kwargs)
    return List(**defaults)

to_status = partial(filter_result,
                    filter_func=_to_status)
to_status_from_search = partial(filter_result,
                                filter_func=_to_status_from_search)
to_direct_message = partial(filter_result,
                            filter_func=_to_direct_message)
to_user = partial(filter_result,
                  filter_func=_to_user)
to_list = partial(filter_result,
                  filter_func=_to_list)


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

    @to_status_from_search
    @include_entities
    def search(self, text, **kwargs):
        return self._api.search(text, **kwargs)

    @to_status
    @include_entities
    def get_retweets_of_me(self, **kwargs):
        return self._api.retweets_of_me(**kwargs)

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

    @to_list
    def get_lists(self, screen_name):
        return self._api.lists(screen_name)

    @to_list
    def get_own_lists(self):
        return self._api.lists()

    @to_list
    def get_list_memberships(self):
        return self._api.lists_memberships()

    @to_list
    def get_list_subscriptions(self):
        return self._api.lists_subscriptions()

    @to_status
    def get_list_timeline(self, a_list):
        owner = a_list.owner.screen_name
        return self._api.list_timeline(owner=owner, slug=a_list.slug)

    @to_user
    def get_list_members(self, a_list):
        owner = a_list.owner.screen_name
        return self._api.list_members(owner=owner, slug=a_list.slug)

    def is_list_member(self, user, a_list):
        return bool(self._api.is_list_member(owner=user.screen_name,
                                             slug=a_list.slug,
                                             user_id=user.id,))

    @to_list
    def subscribe_to_list(self, a_list):
        owner = a_list.owner
        return self._api.subscribe_list(owner=owner.screen_name,
                                        slug=a_list.slug)

    @to_user
    def get_list_subscribers(self, a_list):
        owner = a_list.owner
        return self._api.list_subscribers(owner=owner.screen_name,
                                          slug=a_list.slug,)

    def is_list_subscriber(self, user, a_list):
        return bool(self._api.is_subscribed_list(owner=user.screen_name,
                                                 slug=a_list.slug,
                                                 user_id=user.id,))
