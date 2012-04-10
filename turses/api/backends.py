# -*- coding: utf-8 -*-

"""
turses.api.backends
~~~~~~~~~~~~~~~~~~~

This module contains implementations of `turses.api.base.Api` using multiple
API backends.
"""

# `tweepy`
from tweepy import API as BaseTweepyApi
from tweepy import OAuthHandler as TweepyOAuthHandler

from .base import Api
from ..models import User, Status, DirectMessage
from ..utils import timestamp_from_datetime


class TweepyApi(BaseTweepyApi, Api):
    """
    A `Api` implementation using `tweepy` library.
    
        http://github.com/tweepy/tweepy/ 
    """

    def __init__(self, *args, **kwargs):
        Api.__init__(self, *args, **kwargs)

    # conversion to `turses.models`

    def _to_status(self, statuses):
        def to_status(status):
            kwargs = {
                'id': status.id,
                'created_at_in_seconds': timestamp_from_datetime(status.created_at),
                'user': status.user.screen_name,
                'text': status.text,
            }
            return Status(**kwargs)

        if isinstance(statuses, list):
            return [to_status(status) for status in list(statuses)]
        else:
            return to_status(statuses)

    def _to_direct_message(self, dms):
        def to_direct_message(dm):
            return DirectMessage(id=dm.id,
                                 created_at_in_seconds=timestamp_from_datetime(dm.created_at),
                                 sender_screen_name=dm.sender_screen_name,
                                 recipient_screen_name=dm.recipient_screen_name,
                                 text=dm.text)

        if isinstance(dms, list):
            return [to_direct_message(dm) for dm in list(dms)]
        else:
            return to_direct_message(dms)

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

    def get_home_timeline(self):
        return self._to_status(self._api.home_timeline())

    def get_user_timeline(self, screen_name):
        return self._to_status(self._api.user_timeline(screen_name))

    def get_mentions(self):
        return self._to_status(self._api.mentions())

    def get_favorites(self):
        return self._to_status(self._api.favorites())

    def get_direct_messages(self):
        dms = self._api.direct_messages()
        dms.extend(self._api.sent_direct_messages())
        return self._to_direct_message(dms)
        
    def get_search(self, text):
        # `tweepy.API.search` returns `tweepy.models.SearchResult` objects instead
        # `tweepy.models.Status` so we have to convert them differently
        def to_status(status):
            kwargs = {
                'id': status.id,
                'created_at_in_seconds': timestamp_from_datetime(status.created_at),
                'user': status.from_user,
                'text': status.text,
            }
            return Status(**kwargs)

        results = self._api.search(text)
        return [to_status(result) for result in results]

    def update(self, text):
        return self._api.update_status(text)

    def destroy_status(self, status):
        return self._to_status(self._api.destroy_status(status.id))

    def retweet(self, status):
        return self._to_status(self._api.retweet(status.id))

    def direct_message(self, username, text):
        return self._to_direct_message(self._api.send_direct_message(user=username,
                                                                     text=text))

    def destroy_direct_message(self, dm):
        return self._to_direct_message(self._api.destroy_direct_message(dm.id))

    # TODO: convert to `turses.models.User`
    def create_friendship(self, screen_name):
        self._api.create_friendship(screen_name=screen_name)

    def destroy_friendship(self, screen_name):
        self._api.destroy_friendship(screen_name=screen_name)

    def create_favorite(self, status):
        self._to_status(self._api.create_favorite(status.id))

    def destroy_favorite(self, status):
        self._to_status(self._api.destroy_favorite(status.id))
