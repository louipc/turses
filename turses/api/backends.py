# -*- coding: utf-8 -*-

"""
turses.api.backends
~~~~~~~~~~~~~~~~~~~

This module contains implementations of `turses.api.base.Api` using multiple
API backends.
"""

import os
import sys
import urllib2
import oauth2 as oauth
try:
    import json
except ImportError:
    import simplejson as json


from twitter import Api as BasePythonTwitterApi
from twitter import Status as BaseStatus
from twitter import TwitterError, _FileCache

from .base import Api
from ..models import User, Status, DirectMessage
from ..models import is_DM


DEFAULT_CACHE = object()


# using python-twitter library
class PythonTwitterApi(BasePythonTwitterApi, Api):
    """
    A `Api` implementation using `python-twitter` library.
    
        http://code.google.com/p/python-twitter/
    """

    def __init__(self,
                 consumer_key=None,
                 consumer_secret=None,
                 access_token_key=None,
                 access_token_secret=None,
                 input_encoding=None,
                 request_headers=None,
                 cache=DEFAULT_CACHE,
                 shortner=None,
                 base_url=None,
                 use_gzip_compression=False,
                 debugHTTP=False,
                 proxy={}):
        Api.__init__(self,
                     consumer_key,
                     consumer_secret,
                     access_token_key,
                     access_token_secret,)

        self.SetCache(cache)

        self._urllib         = urllib2
        self._cache_timeout  = PythonTwitterApi.DEFAULT_CACHE_TIMEOUT
        self._input_encoding = input_encoding
        self._use_gzip       = use_gzip_compression
        self._debugHTTP      = debugHTTP
        self._oauth_consumer = None
        self._proxy = proxy

        self._InitializeRequestHeaders(request_headers)
        self._InitializeUserAgent()
        self._InitializeDefaultParameters()

        if base_url is None:
            self.base_url = 'https://api.twitter.com/1'
        else:
            self.base_url = base_url

        if consumer_key is not None and (access_token_key is None or
                                         access_token_secret is None):
            print >> sys.stderr, 'Twitter now requires an oAuth Access Token for API calls.'
            print >> sys.stderr, 'If your using this library from a command line utility, please'
            print >> sys.stderr, 'run the the included get_access_token.py tool to generate one.'

            raise TwitterError('Twitter requires oAuth Access Token for all API access')

        self.SetCredentials(consumer_key, 
                            consumer_secret, 
                            access_token_key, 
                            access_token_secret)
        self.is_authenticated = True


    def _FetchUrl(self,
                  url,
                  post_data=None,
                  parameters=None,
                  no_cache=None,
                  use_gzip_compression=None):
        # Build the extra parameters dict
        extra_params = {}
        if self._default_params:
            extra_params.update(self._default_params)
        if parameters:
            extra_params.update(parameters)

        if post_data:
            http_method = "POST"
        else:
            http_method = "GET"

        if self._debugHTTP:
            _debug = 1
        else:
            _debug = 0

        http_handler = self._urllib.HTTPHandler(debuglevel=_debug)
        https_handler = self._urllib.HTTPSHandler(debuglevel=_debug)
        proxy_handler = self._urllib.ProxyHandler(self._proxy)

        opener = self._urllib.OpenerDirector()
        opener.add_handler(http_handler)
        opener.add_handler(https_handler)

        if self._proxy:
            opener.add_handler(proxy_handler)

        if use_gzip_compression is None:
          use_gzip = self._use_gzip
        else:
          use_gzip = use_gzip_compression

        # Set up compression
        if use_gzip and not post_data:
            opener.addheaders.append(('Accept-Encoding', 'gzip'))

        if self._oauth_consumer is not None:
            if post_data and http_method == "POST":
                parameters = post_data.copy()

            req = oauth.Request.from_consumer_and_token(self._oauth_consumer,
                                                  token=self._oauth_token,
                                                  http_method=http_method,
                                                  http_url=url, parameters=parameters)
            req.sign_request(self._signature_method_hmac_sha1, 
                             self._oauth_consumer, 
                             self._oauth_token)
            #headers = req.to_header()

            if http_method == "POST":
                encoded_post_data = req.to_postdata()
            else:
                encoded_post_data = None
                url = req.to_url()
        else:
            url = self._BuildUrl(url, extra_params=extra_params)
            encoded_post_data = self._EncodePostData(post_data)

        # Open and return the URL immediately if we're not going to cache
        if encoded_post_data or no_cache or not self._cache or not self._cache_timeout:
            response = opener.open(url, encoded_post_data)
            url_data = self._DecompressGzippedResponse(response)
            opener.close()
        else:
        # Unique keys are a combination of the url and the oAuth Consumer Key
            pass
            #if self._consumer_key:
                #key = self._consumer_key + ':' + url
            #else:
                #key = url

        # If the cached version is outdated then fetch another and store it
        # if not last_cached or time.time() >= last_cached + self._cache_timeout:
        try:
            response = opener.open(url, encoded_post_data)
            url_data = self._DecompressGzippedResponse(response)
        #self._cache.Set(key, url_data)
        except urllib2.HTTPError, e:
            print e
        opener.close()
        #else:
          #url_data = self._cache.Get(key)

        # Always return the latest version
        return url_data

    def PostRetweet(self, id):
        # This code comes from issue #130 on python-twitter tracker.
        if not self._oauth_consumer:
            raise TwitterError("The twitter.Api instance must be authenticated.")
        try:
            if int(id) <= 0:
                raise TwitterError("'id' must be a positive number")
        except ValueError:
            raise TwitterError("'id' must be an integer")
        url = 'http://api.twitter.com/1/statuses/retweet/%s.json' % id
        json_data = self._FetchUrl(url, post_data={'dummy': None})
        data = json.loads(json_data)
        self._CheckForTwitterError(data)
        return BaseStatus.NewFromJsonDict(data)

    def GetCachedTime(self, key):
        path = self._GetPath(key)
        if os.path.exists(path):
            return os.path.getmtime(path)
        else:
            return None

    def SetCache(self, cache):
        """
        Override the default cache. Set to None to prevent caching.

        Args:
          cache:
            An instance that supports the same API as the twitter._FileCache
        """
        if cache == DEFAULT_CACHE:
            self._cache = _FileCache()
        else:
            self._cache = cache

    def verify_credentials(self):
        user = self.VerifyCredentials()
        return User(user.screen_name)

    def _to_statuses(self, statuses):
        def to_status(status):
            kwargs = {
                'id': status.id, 
                'created_at_in_seconds': status.created_at_in_seconds,
                'user': status.user.screen_name,
                'text': status.text,
            }

            if (status.favorited):
                kwargs['is_favorite'] = True
            elif (status.retweeted):
                kwargs['is_retweet'] = True
                kwargs['retweet_count'] = int(status.retweet_count)
                kwargs['author'] = status.retweeted_status.user.screen_name

            if (status.in_reply_to_screen_name):
                kwargs['is_reply'] = True 
                kwargs['in_reply_to_user'] = status.in_reply_to_screen_name

            return Status(**kwargs)

        return [to_status(s) for s in statuses]

    def get_home_timeline(self):
        statuses = self.GetFriendsTimeline()
        return self._to_statuses(statuses)

    def get_user_timeline(self, screen_name):
        statuses = self.GetUserTimeline(screen_name, include_rts=True,)
        return self._to_statuses(statuses)

    def get_mentions(self):
        statuses = self.GetMentions()
        return self._to_statuses(statuses)

    def get_favorites(self):
        statuses = self.GetFavorites()
        return self._to_statuses(statuses)

    def get_direct_messages(self):
        dms = self.GetDirectMessages()
        def convert_to_dm(dm):
            return DirectMessage(id=dm.id,
                                 created_at_in_seconds=dm.created_at_in_seconds,
                                 sender_screen_name=dm.sender_screen_name,
                                 recipient_screen_name=dm.recipient_screen_name,
                                 text=dm.text)

        return [convert_to_dm(dm) for dm in dms]

    def get_search(self, text):
        return self._to_statuses(self.GetSearch(text))

    def update(self, text):
        try:
            res = self.PostUpdate(text)
        except TwitterError:
            # Frequently while using `python-twitter` to update the state
            # it raises the "Status is a duplicate" Twitter error
            pass
        else:
            return res

    def retweet(self, status):
        self.PostRetweet(status.id)

    def destroy(self, status):
        if is_DM(status):
            destroy = self.DestroyDirectMessage
        else:
            destroy = self.DestroyStatus

        try:
            res = destroy(status.id)
        except TwitterError:
            pass
        else:
            return res

    def direct_message(self, username, text):
        try:
            self.PostDirectMessage(username, text)
        except TwitterError:
            # It raises the "Status is a duplicate" Twitter error
            # all the time even when sending the messages...
            pass

    def create_friendship(self, screen_name):
        self.CreateFriendship(screen_name)

    def destroy_friendship(self, screen_name):
        self.DestroyFriendship(screen_name)

    def create_favorite(self, status):
        _status = BaseStatus()
        _status.id = status.id
        try:
            self.CreateFavorite(_status)
        except TwitterError:
            pass

    def destroy_favorite(self, status):
        _status = BaseStatus()
        _status.id = status.id
        self.DestroyFavorite(status)
