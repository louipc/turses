# -*- coding: utf-8 -*-

"""
This module contains an `ApiAdapter` abstract class that acts as an adapter
for different Twitter API implementations.

It also contains `AsyncApi`, an asynchronous wrapper to `ApiAdapter` and a
function to authorize `turses` to use a Twitter account obtaining the OAuth
tokens.
"""

from abc import ABCMeta, abstractmethod
import oauth2 as oauth
from urlparse import parse_qsl, urljoin
from gettext import gettext as _

from turses.models import is_DM
from turses.utils import encode
from turses.meta import async, wrap_exceptions


TWITTER_CONSUMER_KEY = 'OEn4hrNGknVz9ozQytoR0A'
TWITTER_CONSUMER_SECRET = 'viud49uVgdVO9dnOGxSQJRo7jphTioIlEn3OdpkZI'

BASE_URL = 'https://api.twitter.com'

HTTP_OK = 200


def get_authorization_tokens():
    """
    Authorize `turses` to use a Twitter account.

    Return a dictionary with `oauth_token` and `oauth_token_secret` keys
    if succesfull, `None` otherwise.
    """
    # This function is borrowed from python-twitter developers
    #
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
    oauth_consumer = oauth.Consumer(key=TWITTER_CONSUMER_KEY,
                                    secret=TWITTER_CONSUMER_SECRET)
    oauth_client = oauth.Client(oauth_consumer)

    print _('Requesting temporary token from Twitter')

    try:
        oauth_token, oauth_token_secret = get_temporary_tokens(oauth_client)
    except Exception as e:
        print e
        return None


    authorization_url = urljoin(BASE_URL, '/oauth/authorize')
    authorization_url_with_token = urljoin(authorization_url,
                                           '?oauth_token=%s' % oauth_token)
    print
    print  _('Please visit the following page to retrieve the pin code needed '
             'to obtain an Authorization Token:')
    print
    print authorization_url_with_token
    print

    pin_code = raw_input(_('Pin code? '))

    print
    print encode(_('Generating and signing request for an access token'))
    print

    # Generate an OAuth token that verifies the identity of the user
    token = oauth.Token(oauth_token, oauth_token_secret)
    token.set_verifier(pin_code)

    # Re-create the OAuth client with the corresponding token
    oauth_client = oauth.Client(oauth_consumer, token)

    try:
        access_tokens = get_access_tokens(oauth_client, pin_code)
        return access_tokens
    except Exception as e:
        print e
        return None

def get_temporary_tokens(oauth_client):
    """
    Request temporary OAuth tokens using the provided `oauth_client`; these
    tokens require the user to confirm its identity on Twitter's website for
    obtaining an access token.

    This function will return a tuple with a public and a private OAuth tokens
    that can be used to retrieve an access token from Twitter if the request
    was successfull.

    If there is an error with the HTTP request, it will raise an
    :class:`Exception` with a meaningful error message.
    """
    request_token_url = urljoin(BASE_URL, '/oauth/request_token')

    response, content = oauth_client.request(request_token_url, 'GET')

    status_code = int(response['status'])
    if status_code == HTTP_OK:
        response_content = dict(parse_qsl(content))

        oauth_token = response_content['oauth_token']
        oauth_token_secret = response_content['oauth_token_secret']

        return (oauth_token, oauth_token_secret)
    else:
        error_message = _('Twitter responded with an HTTP %s code.' % str(status_code))
        raise Exception(error_message)

def get_access_tokens(oauth_client, pin_code):
    """
    Request access tokens using the provided `oauth_client` and the
    `pin_code`that verifies the user's identity.

    This function will return a dictionary with `oauth_token` and
    `oauth_token_secret` keys if the request was successful.

    If there is an error with the HTTP request, it will raise an
    :class:`Exception` with a meaningful error message.
    """
    access_token_url = urljoin(BASE_URL, '/oauth/access_token')

    response, content = oauth_client.request(access_token_url,
                                             method='POST',
                                             body='oauth_verifier=%s' % pin_code)

    status_code = int(response['status'])

    if status_code == HTTP_OK:
        access_token = dict(parse_qsl(content))
        return access_token
    else:
        error_message = _('Twitter responded with an HTTP %s code.' % str(status_code))
        raise Exception(error_message)



class ApiAdapter(object):
    """
    A simplified version of the API to use as an adapter for a real
    implementation.
    """
    __metaclass__ = ABCMeta

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

    @abstractmethod
    def init_api(self):
        pass

    @abstractmethod
    def verify_credentials(self):
        """
        Return a `turses.models.User` with the authenticating user if the given
        credentials are valid.
        """
        pass

    # users

    @abstractmethod
    def get_user(self, screen_name):
        pass

    # timelines

    @abstractmethod
    def get_status(self, status_id):
        pass

    @abstractmethod
    def get_home_timeline(self):
        pass

    @abstractmethod
    def get_user_timeline(self, screen_name):
        pass

    @abstractmethod
    def get_own_timeline(self):
        pass

    @abstractmethod
    def get_mentions(self):
        pass

    @abstractmethod
    def get_favorites(self):
        pass

    @abstractmethod
    def get_direct_messages(self):
        pass

    @abstractmethod
    def get_thread(self, status):
        pass

    @abstractmethod
    def get_message_thread(self, dm):
        pass

    @abstractmethod
    def search(self, text):
        pass

    @abstractmethod
    def get_retweets_of_me(self):
        pass

    # statuses

    @abstractmethod
    def update(self, text):
        pass

    @abstractmethod
    def retweet(self, status):
        pass

    @abstractmethod
    def destroy_status(self, status):
        """
        Destroy the given `status` (must belong to authenticating user).
        """
        pass

    @abstractmethod
    def direct_message(self, screen_name, text):
        pass

    @abstractmethod
    def destroy_direct_message(self, dm):
        """
        Destroy the given `dm` (must be written by the authenticating user).
        """
        pass

    # friendship

    @abstractmethod
    def create_friendship(self, screen_name):
        pass

    @abstractmethod
    def destroy_friendship(self, screen_name):
        pass

    # favorite methods

    @abstractmethod
    def create_favorite(self, status):
        pass

    @abstractmethod
    def destroy_favorite(self, status):
        pass

    # list methods

    @abstractmethod
    def get_lists(self, screen_name):
        pass

    @abstractmethod
    def get_own_lists(self):
        pass

    @abstractmethod
    def get_list_memberships(self):
        pass

    @abstractmethod
    def get_list_subscriptions(self):
        pass

    @abstractmethod
    def get_list_timeline(self, list):
        pass

    @abstractmethod
    def get_list_members(self, list):
        pass

    @abstractmethod
    def is_list_member(self, user, list):
        pass

    @abstractmethod
    def subscribe_to_list(self, list):
        pass

    @abstractmethod
    def get_list_subscribers(self, list):
        pass

    @abstractmethod
    def is_list_subscriber(self, user, list):
        pass


class AsyncApi(ApiAdapter):
    """
    Wrap an `ApiAdapter` subclass and execute the methods for creating,
    updating and deleting Twitter entities in background. Those methods
    are decorated with `turses.utils.wrap_exceptions`.
    """

    def __init__(self, api_cls, *args, **kwargs):
        """
        Args:
            api_cls -- the class used to instantiate the Twitter API,
                       it must implement the methods in `ApiAdapter`.
        """
        ApiAdapter.__init__(self, *args, **kwargs)
        self._api = api_cls(access_token_key=self._access_token_key,
                            access_token_secret=self._access_token_secret,)

    @wrap_exceptions
    def init_api(self):
        self._api.init_api()
        self.is_authenticated = True
        self.user = self.verify_credentials()

    def verify_credentials(self):
        return self._api.verify_credentials()

    def get_status(self, **kwargs):
        return self._api.get_status(**kwargs)

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

    def get_message_thread(self, dm, **kwargs):
        return self._api.get_message_thread(dm, **kwargs)

    def search(self, text, **kwargs):
        return self._api.search(text, **kwargs)

    def get_retweets_of_me(self, **kwargs):
        return self._api.get_retweets_of_me(**kwargs)

    def get_user(self, screen_name):
        return self._api.get_user(screen_name)

    @async
    @wrap_exceptions
    def update(self, text):
        self._api.update(text)

    @async
    @wrap_exceptions
    def retweet(self, status):
        self._api.retweet(status)

    @async
    @wrap_exceptions
    def destroy_status(self, status):
        self._api.destroy_status(status)

    @async
    @wrap_exceptions
    def destroy_direct_message(self, status):
        self._api.destroy_direct_message(status)

    @async
    @wrap_exceptions
    def direct_message(self, screen_name, text):
        self._api.direct_message(screen_name, text)

    @async
    @wrap_exceptions
    def create_friendship(self, screen_name):
        self._api.create_friendship(screen_name)

    @async
    @wrap_exceptions
    def destroy_friendship(self, screen_name):
        self._api.destroy_friendship(screen_name)

    @async
    @wrap_exceptions
    def create_favorite(self, status):
        if is_DM(status) or status.is_favorite:
            raise Exception
        self._api.create_favorite(status)

    @async
    @wrap_exceptions
    def destroy_favorite(self, status):
        self._api.destroy_favorite(status)

    def get_list(self, screen_name, slug):
        pass

    def get_lists(self, screen_name):
        pass

    def get_own_lists(self):
        pass

    def get_list_memberships(self):
        pass

    def get_list_subscriptions(self):
        pass

    def get_list_timeline(self, list):
        pass

    def get_list_members(self, list):
        pass

    def is_list_member(self, user, list):
        pass

    def subscribe_to_list(self, list):
        pass

    def get_list_subscribers(self, list):
        pass

    def is_list_subscriber(self, user, list):
        pass
