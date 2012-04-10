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


twitter_consumer_key = 'OEn4hrNGknVz9ozQytoR0A'
twitter_consumer_secret = 'viud49uVgdVO9dnOGxSQJRo7jphTioIlEn3OdpkZI'


class Api(object):
    """
    A simplified version of the API to use as a mediator for a real
    implementation.
    """

    def __init__(self,
                 access_token_key,
                 access_token_secret,
                 consumer_key=twitter_consumer_key,
                 consumer_secret=twitter_consumer_secret,):
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._access_token_key = access_token_key
        self._access_token_secret = access_token_secret
        self.is_authenticated = False

    def init_api(self): 
        raise NotImplementedError

    def verify_credentials(self):
        """
        Return a `turses.models.User` with the authenticating user if the given 
        credentials are valid.
        """
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

    def get_thread(self, status):
        raise NotImplementedError

    def search(self, text):
        raise NotImplementedError

    def update(self, text): 
        raise NotImplementedError

    def retweet(self, status): 
        raise NotImplementedError

    def destroy_status(self, status):
        """
        Destroy the given `status` (must belong to authenticating user).
        """
        raise NotImplementedError

    def direct_message(self, screen_name, text):
        raise NotImplementedError

    def destroy_direct_message(self, dm):
        """
        Destroy the given `dm` (must be written by the authenticating user).
        """
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
        self._api = api_cls(access_token_key=self._access_token_key,
                            access_token_secret=self._access_token_secret,)

    @wrap_exceptions
    def init_api(self):
        self._api.init_api()
        self.is_authenticated = True
        self.user = self.verify_credentials()

    def verify_credentials(self):
        return self._api.verify_credentials()

    def get_home_timeline(self):
        return self._api.get_home_timeline()

    def get_user_timeline(self, screen_name):
        return self._api.get_user_timeline(screen_name=screen_name)

    def get_own_timeline(self):
        return self._api.get_user_timeline(screen_name=self.user.screen_name)

    def get_mentions(self):
        return self._api.get_mentions()

    def get_favorites(self):
        return self._api.get_favorites()

    def get_direct_messages(self):
        return self._api.get_direct_messages()

    def get_thread(self, status):
        return self._api.get_own_timeline()

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
    def destroy_status(self, status):
        args = status,
        destroy_thread = Thread(target=self._api.destroy_status, args=args)
        destroy_thread.start()

    @wrap_exceptions
    def destroy_direct_message(self, status):
        args = status,
        destroy_thread = Thread(target=self._api.destroy_direct_message, args=args)
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
        args = status,
        unfavorite_thread = Thread(target=self._api.destroy_favorite, args=args)
        unfavorite_thread.start()
