# -*- coding: utf-8 -*-

"""
turses.api.base
~~~~~~~~~~~~~~~

This module contains an interface to the Twitter API that acts as a mediator
for different implementations.

It also contains an asynchronous wrapper to `Api`.
"""

from threading import Thread

from ..decorators import wrap_exceptions
from ..models import is_DM


class Api(object):
    """
    A simplified version of the API to use as a mediator for a real
    implementation.
    """

    def __init__(self,
                 consumer_key,
                 consumer_secret,
                 access_token_key,
                 access_token_secret,):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token_key = access_token_key
        self._access_token_secret = access_token_secret
        self.is_authenticated = False

    def init_api(self): 
        raise NotImplementedError

    def verify_credentials(self):
        raise NotImplementedError

    def get_home_timeline(self): 
        raise NotImplementedError

    def get_user_timeline(self, screen_name):
        raise NotImplementedError

    def get_own_timeline(self):
        raise NotImplementedError

    def get_mentions(self): 
        raise NotImplementedError

    def get_favorites(self):
        raise NotImplementedError

    def get_direct_messages(self):
        raise NotImplementedError

    def search(self, text):
        raise NotImplementedError

    def update(self, text): 
        raise NotImplementedError

    def retweet(self, status): 
        raise NotImplementedError

    def destroy(self, status):
        raise NotImplementedError

    def direct_message(self, screen_name, text):
        raise NotImplementedError

    def create_friendship(self, screen_name): 
        raise NotImplementedError

    def destroy_friendship(self, screen_name):
        raise NotImplementedError

    def create_favorite(self, status):
        raise NotImplementedError

    def destroy_favorite(self, status): 
        raise NotImplementedError


class AsyncApi(Api):
    """
    Implementation of `Api` that executes most of the API calls in
    background and provides `on_error` and `on_success` callbacks for every
    method.
    """

    def __init__(self, api_cls, *args, **kwargs):
        """
        It adds the `api_cls` argument to the `Api` object constructor.

        `api_cls` is the class used to instantiate the Twitter API,
        it must implement the methods in `Api`.
        """
        Api.__init__(self, *args, **kwargs)
        self._api_cls = api_cls

    @wrap_exceptions
    def init_api(self):
        self._api = self._api_cls(consumer_key=self._consumer_key,
                                  consumer_secret=self._consumer_secret,
                                  access_token_key=self._access_token_key,
                                  access_token_secret=self._access_token_secret,)
        self.is_authenticated = True
        self.user = self.verify_credentials()

    def verify_credentials(self):
        return self._api.verify_credentials()

    @wrap_exceptions
    def get_home_timeline(self):
        return self._api.get_home_timeline()

    @wrap_exceptions
    def get_user_timeline(self, screen_name):
        return self._api.get_user_timeline(screen_name=screen_name)

    @wrap_exceptions
    def get_own_timeline(self):
        return self._api.get_user_timeline(screen_name=self.user.screen_name)

    @wrap_exceptions
    def get_mentions(self):
        return self._api.get_mentions()

    @wrap_exceptions
    def get_favorites(self):
        return self._api.get_favorites()

    @wrap_exceptions
    def get_direct_messages(self):
        return self._api.get_direct_messages()

    @wrap_exceptions
    def search(self, text):
        return self._api.get_search(text)

    @wrap_exceptions
    def update(self, text):
        args = text,
        update_thread = Thread(target=self._api.update, args=args)
        update_thread.start()

    @wrap_exceptions
    def retweet(self, status):
        args = status,
        retweet_thread = Thread(target=self._api.retweet, args=args)
        retweet_thread.start()

    @wrap_exceptions
    def destroy(self, status):
        args = status,
        destroy_thread = Thread(target=self._api.destroy, args=args)
        destroy_thread.start()

    @wrap_exceptions
    def direct_message(self, screen_name, text):
        args = (screen_name, text,)
        dm_thread = Thread(target=self._api.direct_message, args=args)
        dm_thread.start()

    @wrap_exceptions
    def create_friendship(self, screen_name):
        args = screen_name,
        follow_thread = Thread(target=self._api.create_friendship, args=args)
        follow_thread.start()

    @wrap_exceptions
    def destroy_friendship(self, screen_name):
        args = screen_name,
        unfollow_thread = Thread(target=self._api.destroy_friendship, args=args)
        unfollow_thread.start()

    @wrap_exceptions
    def create_favorite(self, status):
        if is_DM(status) or status.is_favorite:
            raise Exception
        args = status,
        favorite_thread = Thread(target=self._api.create_favorite, args=args)
        favorite_thread.start()

    @wrap_exceptions
    def destroy_favorite(self, status):
        if is_DM(status) or not status.is_favorite:
            raise Exception
        args = status,
        unfavorite_thread = Thread(target=self._api.destroy_favorite, args=args)
        unfavorite_thread.start()
