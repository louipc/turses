# -*- coding: utf-8 -*-

"""
turses.api.base
~~~~~~~~~~~~~~~

This module contains an interface to the Twitter API that acts as a mediator
for different implementations.

It also contains an asynchronous wrapper to `Api`.
"""

import oauth2 as oauth
from threading import Thread
from urlparse import parse_qsl
from gettext import gettext as _

from ..models import is_DM
from ..utils import encode, wrap_exceptions


TWITTER_CONSUMER_KEY = 'OEn4hrNGknVz9ozQytoR0A'
TWITTER_CONSUMER_SECRET = 'viud49uVgdVO9dnOGxSQJRo7jphTioIlEn3OdpkZI'

BASE_URL = 'https://api.twitter.com'

def authorization():
    """
    Authorize `turses` to use a Twitter account. 

    Return a dictionary with `oauth_token` and `oauth_token_secret`
    if succesfull, `None` otherwise.
    """
    # This function is borrowed from python-twitter developers 

    # Copyright 2007 The Python-Twitter Developers
    #
    # Licensed under the Apache License, Version 2.0 (the "License");
    # you may not use this file except in compliance with the License.
    # You may obtain a copy of the License at
    #
    #     http://www.apache.org/licenses/LICENSE-2.0
    #
    # Unless required by applicable law or agreed to in writing, software
    # distributed under the License is distributed on an "AS IS" BASIS,
    # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    # See the License for the specific language governing permissions and
    # limitations under the License.
    print 'base_url:{0}'.format(BASE_URL)


    REQUEST_TOKEN_URL = BASE_URL + '/oauth/request_token'
    ACCESS_TOKEN_URL  = BASE_URL + '/oauth/access_token'
    AUTHORIZATION_URL = BASE_URL + '/oauth/authorize'
    consumer_key      = TWITTER_CONSUMER_KEY
    consumer_secret   = TWITTER_CONSUMER_SECRET
    oauth_consumer    = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_client      = oauth.Client(oauth_consumer)

    print encode(_('Requesting temp token from Twitter'))

    resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

    if resp['status'] != '200':
        print encode(_('Invalid respond, requesting temp token: %s')) % str(resp['status'])
        return

    request_token = dict(parse_qsl(content))

    print ''
    print encode(_('Please visit the following page to retrieve needed pin code'))
    print encode(_('to obtain an Authentication Token:'))
    print ''
    print '%s?oauth_token=%s' % (AUTHORIZATION_URL, request_token['oauth_token'])
    print ''

    pincode = raw_input('Pin code? ')

    token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
    token.set_verifier(pincode)

    print ''
    print encode(_('Generating and signing request for an access token'))
    print ''

    oauth_client  = oauth.Client(oauth_consumer, token)
    resp, content = oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % pincode)
    access_token  = dict(parse_qsl(content))

    if resp['status'] == '200':
        return access_token
    else:
        print 'response:{0}'.format(resp['status'])
        print encode(_('Request for access token failed: %s')) % resp['status']
        return None


class Api(object):
    """
    A simplified version of the API to use as a mediator for a real
    implementation.
    """

    def __init__(self,
                 access_token_key,
                 access_token_secret,
                 consumer_key=TWITTER_CONSUMER_KEY,
                 consumer_secret=TWITTER_CONSUMER_SECRET,):
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

    # timelines

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

    # statuses

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

    # friendship

    def create_friendship(self, screen_name): 
        raise NotImplementedError

    def destroy_friendship(self, screen_name):
        raise NotImplementedError

    # favorite methods

    def create_favorite(self, status):
        raise NotImplementedError

    def destroy_favorite(self, status): 
        raise NotImplementedError

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

    def get_home_timeline(self, **kwargs):
        return self._api.get_home_timeline(**kwargs)

    def get_user_timeline(self, screen_name, **kwargs):
        return self._api.get_user_timeline(screen_name=screen_name, **kwargs)

    def get_own_timeline(self, **kwargs):
        return self._api.get_own_timeline(**kwargs)

    def get_mentions(self, **kwargs):
        return self._api.get_mentions()

    def get_favorites(self, **kwargs):
        return self._api.get_favorites()

    def get_direct_messages(self, **kwargs):
        return self._api.get_direct_messages(**kwargs)

    def get_thread(self, status, **kwargs):
        return self._api.get_thread(status, **kwargs)

    def get_search(self, text, **kwargs):
        return self._api.get_search(text, **kwargs)

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
