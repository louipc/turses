# -*- coding: utf-8 -*-

"""
This module contains an `ApiAdapter` abstract class that acts as an adapter
for different Twitter API implementations.

It also contains `AsyncApi`, an asynchronous wrapper to `ApiAdapter` and a
function to authorize `turses` to use a Twitter account obtaining the OAuth
tokens.
"""

from abc import ABCMeta, abstractmethod
from gettext import gettext as _

import tweepy

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

    oauth_client = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY,
                                       TWITTER_CONSUMER_SECRET)

    print _('Requesting temporary token from Twitter')

    try:
        authorization_url_with_token = oauth_client.get_authorization_url()
    except tweepy.TweepError:
        print 'Error! Failed to get request token.'
        return None

    print
    print _('Please visit the following page to retrieve the pin code needed '
            'to obtain an Authorization Token:')
    print
    print authorization_url_with_token
    print

    verifier = raw_input(_('Pin code? '))

    print
    print encode(_('Generating and signing request for an access token'))
    print

    # Use the "pin code"/verifier to authorize to access to the account
    try:
        oauth_client.get_access_token(verifier)
        access_tokens = {}
        access_tokens['oauth_token'] = oauth_client.access_token
        access_tokens['oauth_token_secret'] = oauth_client.access_token_secret
        return access_tokens
    except tweepy.TweepError:
        print 'Error! Failed to get access token.'
        return None


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
    def reply(self, status, text):
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
    def subscribe_to_list(self, list):
        pass

    @abstractmethod
    def get_list_subscribers(self, list):
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
    def reply(self, status, text):
        self._api.reply(status, text)

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

    def subscribe_to_list(self, list):
        pass

    def get_list_subscribers(self, list):
        pass
