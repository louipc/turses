###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import os
import sys
import urllib2
import oauth2 as oauth
from threading import Thread

from twitter import Api as BaseApi 
from twitter import TwitterError, Status, _FileCache

from util import is_DM
from decorators import wrap_exceptions

try:
    import json
except ImportError:
    pass
    #import simplejson as json

DEFAULT_CACHE = object()


# TODO document every method and give it arguments according to the API methods
class TwitterApi(object):
    """
    An adapter for the different libraries that implement the Twitter's API.

    Implements every method in the Twitter's API:
        
        http://dev.twitter.com/docs/api
    """

    # Timelines

    def get_home_timeline(self,
                          count=None,
                          since_id=None,
                          max_id=None,
                          page=None,
                          trim_user=None,
                          include_rts=None,
                          include_entities=None,
                          exclude_replies=None,
                          contributor_details=None):
        """
        Returns the most recent statuses, including retweets if they exist, 
        posted by the authenticating user and the user's they follow. 
        
        This is the same timeline seen by a user when they login to twitter.com.
        """
        raise NotImplementedError

    def get_mentions(self,
                     count=None,
                     since_id=None,
                     max_id=None,
                     page=None,
                     trim_user=None,
                     include_rts=None,
                     include_entities=None,
                     exclude_replies=None,
                     contributor_details=None):
        """
        Returns the 20 most recent mentions (status containing @username) 
        for the authenticating user.

        The timeline returned is the equivalent of the one seen when you view 
        your mentions on twitter.com.
        """
        raise NotImplementedError

    def get_retweeted_by_me(self,
                            count=None,
                            since_id=None,
                            max_id=None,
                            page=None,
                            trim_user=None,
                            include_entities=None):
        """
        Returns the 20 most recent retweets posted by the authenticating user.
        """
        raise NotImplementedError

    def get_retweeted_to_me(self,
                            count=None,
                            since_id=None,
                            max_id=None,
                            page=None,
                            trim_user=None,
                            include_entities=None):
        """
        Returns the 20 most recent retweets posted by users the authenticating 
        user follow.
        """
        raise NotImplementedError

    def get_retweeted_of_me(self,
                            count=None,
                            since_id=None,
                            max_id=None,
                            page=None,
                            trim_user=None,
                            include_entities=None):
        """
        Returns the 20 most recent tweets of the authenticated user that have 
        been retweeted by others.
        """
        raise NotImplementedError

    def get_user_timeline(self,
                          user_id=None,
                          screen_name=None,
                          since_id=None,
                          count=None,
                          max_id=None,
                          page=None,
                          trim_user=None,
                          include_rts=None,
                          include_entities=None,
                          exclude_replies=None,
                          contributor_details=None):
        """
        Returns the 20 most recent statuses posted by the authenticating user. 
        It is also possible to request another user's timeline by using the 
        screen_name or user_id parameter. 
        
        The other users timeline will only be visible if they are not protected, 
        or if the authenticating user's follow request was accepted by the 
        protected user.
         
        The timeline returned is the equivalent of the one seen when you view 
        a user's profile on twitter.com.
        """
        raise NotImplementedError

    def get_own_tweets(self):
        return self.get_user_timeline()

    def get_retweeted_to_user(self, username):
        raise NotImplementedError

    def get_retweeted_by_user(self, username):
        raise NotImplementedError

    # Tweets

    def get_retweeted_by(self, status):
        """Returns a list with the users that retweeted `status`."""
        raise NotImplementedError

    def get_retweeted_by_ids(self, status):
        """Returns a list of IDs of the users that retweeted `status`."""
        raise NotImplementedError

    def get_retweets(self, status):
        """Returns up to 100 of the first retweets of `status`."""
        raise NotImplementedError

    def get_status_by_id(self, id):
        """Returns a single status, specified by the `id` parameter."""
        raise NotImplementedError

    def destroy(self, status):
        """
        Destroy the given `status`. The authenticated user must be the 
        author of the specified status.
        """
        raise NotImplementedError

    def retweet(self, status):
        """Retweets the given `status`."""
        raise NotImplementedError

    def update(self, text):
        """Updates the authenticating user's status."""
        raise NotImplementedError

    def update_with_media(self, text):
        """
        Updates the authenticating user's status and attaches media for upload.
        """
        raise NotImplementedError

    # Search

    def search(self, text):
        """Returns tweets that match the specified `text`."""
        raise NotImplementedError

    # Direct Messages

    def get_direct_messages(self):
        """
        Return the 20 most recent direct messages sent to the authenticating
        user.
        """
        raise NotImplementedError

    def get_sent_direct_messages(self):
        """
        Return the 20 most recent direct messages sent by the authenticating
        user.
        """
        raise NotImplementedError

    def destroy_direct_message(self, dm):
        """Deletes the given `dm`."""
        raise NotImplementedError

    def direct_message(self, username, text):
        """
        Sends a new direct message to the specified user from the authenticating 
        user.
        """
        raise NotImplementedError

    def get_direct_message_by_id(self, id):
        """Returns a single direct message, specified by the `id` parameter."""
        raise NotImplementedError

    # Friends & Followers

    def get_followers_ids(self, username):
        """Returns a list of IDs for every user following the specified user."""
        raise NotImplementedError

    def get_friends_ids(self, username):
        """
        Returns a list of IDs for every user the specified user is following.
        """
        raise NotImplementedError

    def friendship_exists(self, a_user, another_user):
        """
        Returns `True` if the user `a_user` follows the `another_user`.
        """
        raise NotImplementedError

    def get_incoming_friendship(self):
        """
        Returns a list of IDs for every user who has a pending request to
        follow the authenticating user.
        """
        raise NotImplementedError

    def get_outgoing_friendship(self):
        """
        Returns a list of IDs for every protected user for whom the 
        authenticating user has a pending request.
        """
        raise NotImplementedError

    def get_friendship(self, a_user, another_user):
        """
        Returns detailed information about the friendship between `a_user`
        and `another_user`.
        """
        raise NotImplementedError

    def create_friendship(self, user_id):
        """
        Allows the authenticating user to follow the user ID specified in the 
        `user_id` parameter. 
        """
        raise NotImplementedError

    def destroy_friendship(self, user_id):
        """
        Allows the authenticating user to unfollow the user ID specified in the 
        `user_id` parameter. 
        """
        raise NotImplementedError

    def lookup_friendship(self, users):
        """
        Returns the relationship of the authenticating user to the specified 
        list of users.
        """
        raise NotImplementedError

    def update_friendship(self, user):
        """
        Allows one to enable or disable retweets and device notifications 
        from the specified `user`.
        """
        raise NotImplementedError

    def get_no_retweets_ids(self):
        """
        Returns an array of user_IDs that the currently authenticated user does 
        not want to see retweets from.
        """
        raise NotImplementedError

    # Users

    def lookup_users(self, users):
        """
        Return information about the given `users` with their most recent
        status (if the authenticated user has permission).
        """
        raise NotImplementedError

    def get_profile_image(self, username):
        """
        Return the profile image for the user with the indicated `username`.
        """
        raise NotImplementedError

    def search_users(self, text):
        """
        Search for `text` in Twitter usernames.
        """
        raise NotImplementedError

    def get_user(self, username):
        """
        Returns information about the user with the given `username` and the
        user's most recent status.
        """
        raise NotImplementedError

    def get_user_contributees(self, username):
        """
        Returns an array of users that the specified user can contribute to.
        """
        raise NotImplementedError

    def get_user_contributors(self, username):
        """
        Returns an array of users who can contribute to the specified user.
        """
        raise NotImplementedError

    # Suggested users

    def get_user_category_suggestions(self):
        """Returns a list of suggested user categories."""
        raise NotImplementedError

    def get_user_suggestions(self, category):
        """
        Access the users in the given `category` of the Twitter suggested user 
        list.
        """
        raise NotImplementedError

    def get_user_suggestions_with_status(self, category):
        """
        Access the users in the given `category` of the Twitter suggested user 
        list with their most recent status.
        """
        raise NotImplementedError

    # Favorites

    def get_favorites(self, user_id):
        """
        Returns the 20 most recent favorite statuses for the authenticating user 
        or user specified by the ID parameter.
        """
        raise NotImplementedError

    def create_favorite(self, status):
        """
        Favorites `status` as the authenticating user.
        """
        raise NotImplementedError

    def destroy_favorite(self, status):
        """
        Un-favorites `status` as the authenticating user.
        """
        raise NotImplementedError

    # Lists

    def get_own_subscribed_lists(self):
        """
        Returns all lists the authenticating subscribes to, including their own.
        """
        raise NotImplementedError

    def get_subscribed_lists(self, user):
        """
        Returns all lists the specified user subscribes to, including their own.
        """
        raise NotImplementedError

    def get_list_statuses(self, list):
        """
        Returns tweet timeline for members of the specified list.
        """
        raise NotImplementedError

    def remove_user_from_list(self, user, list):
        """
        Removes the specified `user` from the `list`. The authenticated user must 
        be the list's owner to remove members from the list.
        """
        raise NotImplementedError

    def get_list_memberships(self, user):
        """
        Returns the lists the specified user has been added to.
        """
        raise NotImplementedError

    def get_own_list_memberships(self):
        """
        Returns the lists the authenticating user has been added to.
        """
        raise NotImplementedError

    def get_list_subscribers(self, list):
        """
        Returns the subscribers of the specified list. Private list subscribers 
        will only be shown if the authenticated user owns the specified list.
        """
        raise NotImplementedError

    def create_list_subscription(self, list):
        """
        Subscribes the authenticated user to the specified list.
        """
        raise NotImplementedError

    def is_subscrided_to_list(self, user, list):
        """
        Check if the specified `user` is a subscriber of the specified `list`. 
        """
        raise NotImplementedError

    def destroy_list_subscription(self, list):
        """
        Unsubscribes the authenticated `user` from the specified `list`.
        """
        raise NotImplementedError

    def add_members_to_list(self, users, list):
        """
        Adds specified `users` to `list`. The authenticated user must own the 
        list to be able to add members to it.
        """
        raise NotImplementedError

    def is_member_of_list(self, user, list):
        """
        Check if the specified `user` is a member of the specified `list`.
        """
        raise NotImplementedError

    def get_list_members(self, list):
        """
        Returns the members of the specified `list`. Private list members will 
        only be shown if the authenticated user owns the specified list.
        """
        raise NotImplementedError

    def add_member_to_list(self, user, list):
        """
        Add `user` to `list`. The authenticated user must own the list to be 
        able to add members to it.
        """
        raise NotImplementedError

    def destroy_list(self, list):
        """
        Deletes the specified `list`. The authenticated user must own the list 
        to be able to destroy it.
        """
        raise NotImplementedError

    def update_list(self, list):
        """
        Updates the specified `list`. The authenticated user must own the list 
        to be able to update it.
        """
        raise NotImplementedError

    def create_list(self, list):
        """
        Creates a new list for the authenticated user.
        """
        raise NotImplementedError

    def get_lists(self, user):
        """
        Returns the lists of the specified `user`. Private lists will be included 
        if the authenticated user is the same as the user whose lists are 
        being returned.
        """
        raise NotImplementedError

    def get_own_lists(self):
        """
        Returns the lists of the authenticated user.
        """
        raise NotImplementedError

    def get_list(self, list):
        """
        Returns the specified `list`. Private lists will only be shown if 
        the authenticated user owns the specified list.
        """
        raise NotImplementedError

    def get_user_subscriptions(self, user):
        """
        Obtain a collection of the lists the specified `user` is subscribed to, 
        does not include the user's own lists.
        """
        raise NotImplementedError

    # Accounts

    def get_rate_limit_status(self):
        """
        Returns the remaining number of API requests available to the requesting 
        user before the API limit is reached for the current hour. 
        """
        raise NotImplementedError

    def verify_credential(self):
        """
        Returns a representation of the requesting user if authentication 
        was successful.
        """
        raise NotImplementedError

    def end_session(self):
        """
        Ends the session of the authenticating user.
        """
        raise NotImplementedError

    def update_profile(self, **kwargs):
        """
        Sets values that users are able to set under the "Account" tab of 
        their settings page.
        """
        raise NotImplementedError

    def update_profile_background_image(self, image):
        """Updates the authenticating user's profile background image."""
        raise NotImplementedError

    def update_profile_colors(self, colors):
        """
        Sets one or more hex values that control the color scheme of the 
        authenticating user's profile page on twitter.com. 
        
        Each parameter's value must be a valid hexidecimal value, and may be 
        either three or six characters (ex: #fff or #ffffff).
        """
        raise NotImplementedError
    
    def update_profile_image(self, image):
        """Updates the authenticating user's profile image."""
        raise NotImplementedError

    def get_totals(self):
        """
        Returns the current count of friends, followers, updates (statuses) and 
        favorites of the authenticating user.
        """
        raise NotImplementedError

    def get_settings(self):
        """
        Returns settings (including current trend, geo and sleep time information) 
        for the authenticating user.
        """
        raise NotImplementedError

    def set_settings(self, settings):
        """
        Updates the authenticated user's settings.
        """
        raise NotImplementedError

    # Notification
    #  SMS-based notifications

    def notifications_follow(self, user):
        """Enables device notifications for updates from the specified `user`."""
        raise NotImplementedError

    def notifications_leave(self, user):
        """Disables device notifications for updates from the specified `user`."""
        raise NotImplementedError

    # Saved Searches

    def get_saved_searches(self):
        """Returns the authenticated user's saved search queries."""
        raise NotImplementedError

    def get_saved_search_by_id(self, id):
        """
        Retrieve the information for the saved search represented by the given 
        `id`. The authenticating user must be the owner of saved search ID 
        being requested."""
        raise NotImplementedError

    def create_saved_search(self):
        """Create a new saved search for the authenticated user."""
        raise NotImplementedError

    def destroy_saved_search(self, id):
        """  
        Destroys a saved search for the authenticating user. The authenticating 
        user must be the owner of saved search `id` being destroyed.
        """
        raise NotImplementedError

    # Places & Geo

    def get_place(self, id):
        """Returns all the information about a known place."""
        raise NotImplementedError

    def reverse_geocode(self, latitude, longitude):
        """
        Given a latitude and a longitude, searches for places that can be used 
        as a place_id when updating a status.
        """
        raise NotImplementedError

    def search_place(self, latitude=None, longitude=None, ip=None, name=None):
        """
        Search for places that can be attached to a statuses/update. 
        
        Given a latitude and a longitude pair, an IP address, or a name, this 
        method will return a list of all the valid places that can be used as the 
        place_id when updating a status.
        """
        raise NotImplementedError

    def get_similar_places(self, latitude, longitude):
        """
        Locates places near the given coordinates which are similar in name.
        """
        raise NotImplementedError

    def create_place(self, latitude, longitude):
        """
        Creates a new place object at the given latitude and longitude.
        """
        raise NotImplementedError

    # Trends 

    def get_trends(self, woeid):
        raise NotImplementedError

    def get_trends_available_locations(self):
        raise NotImplementedError

    def get_daily_trends(self):
        raise NotImplementedError

    def get_weekly_trends(self):
        raise NotImplementedError

    # Block

    def get_blocking(self):
        raise NotImplementedError

    def get_blocking_ids(self):
        raise NotImplementedError

    def is_blocking(self, user):
        raise NotImplementedError

    def block(self, user):
        raise NotImplementedError

    def unblock(self, user):
        raise NotImplementedError

    # Spam

    def report_spam(self, user):
        raise NotImplementedError

    # Oauth

    def oauth_authenticate(self):
        raise NotImplementedError

    def oauth_authorize(self):
        raise NotImplementedError

    def oauth_acces_token(self):
        raise NotImplementedError

    def oauth_request_token(self):
        raise NotImplementedError

    # Help

    def help_test(self):
        raise NotImplementedError

    def help_configuration(self):
        raise NotImplementedError

    def help_languages(self):
        raise NotImplementedError

    # Legal

    def get_privacy_policy(self):
        raise NotImplementedError

    def get_terms_of_service(self):
        raise NotImplementedError


class ApiWrapper(object):
    """
    A simplified version of the API to use as a mediator for a `TwitterApi`
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

    def get_home_timeline(self, 
                          on_error=None, 
                          on_success=None):
        raise NotImplementedError

    def get_mentions(self, 
                     on_error=None, 
                     on_success=None):
        raise NotImplementedError

    def get_favorites(self, 
                      on_error=None, 
                      on_success=None):
        raise NotImplementedError

    def get_direct_messages(self, 
                            on_error=None, 
                            on_success=None):
        raise NotImplementedError

    def search(self, 
               text, 
               on_error=None, 
               on_success=None):
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


# TODO implement the methods of `TwitterApi`
#       and use them from `AsyncApi`
# using python-twitter library
class PythonTwitterApi(BaseApi, TwitterApi):
    """
    A `TwitterApi` implementation using `python-twitter` library.
    
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
        self.SetCache(cache)
        self._urllib         = urllib2
        self._cache_timeout  = BaseApi.DEFAULT_CACHE_TIMEOUT
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

        self.SetCredentials(consumer_key, consumer_secret, access_token_key, access_token_secret)

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
        return Status.NewFromJsonDict(data)

    def GetCachedTime(self,key):
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

    def get_home_timeline(self, *args, **kwargs):
        return self.GetFriendsTimeline(*args, **kwargs)

    def get_mentions(self, *args, **kwargs):
        return self.GetMentions(*args, **kwargs)

    def get_favorites(self, *args, **kwargs):
        return self.GetFavorites()

    def get_direct_messages(self, *args, **kwargs):
        return self.GetDirectMessages()

    def get_search(self, text, *args, **kwargs):
        return self.GetSearch(text)

    def update(self, text, *args, **kwargs):
        return self.PostUpdate(text)

    def retweet(self, status, *args, **kwargs):
        self.PostRetweet(status.id)

    def destroy(self, status, *args, **kwargs):
        if is_DM(status):
            destroy = self.DestroyDirectMessage
        else:
            destroy = self.DestroyStatus
        destroy(status.id)

    def direct_message(self, username, text, *args, **kwargs):
        self.PostDirectMessage(username, text)

    def create_friendship(self, screen_name, *args, **kwargs):
        self.CreateFriendShip(screen_name)

    def destroy_friendship(self, screen_name, *args, **kwargs):
        self.DestroyFriendship(screen_name)

    def create_favorite(self, status, *args, **kwargs):
        self.CreateFavorite(status)

    def destory_favorite(self, status, *args, **kwargs):
        self.DestroyFavorite(status)


class AsyncApi(ApiWrapper):
    """
    Implementation of `ApiWrapper` that executes most of the API calls in
    background and provides `on_error` and `on_success` callbacks for every
    method.
    """

    @wrap_exceptions
    def init_api(self):
        init_thread = Thread(target=self._init_api,)
        init_thread.start()

    def _init_api(self):
        self._api = PythonTwitterApi(consumer_key=self._consumer_key,
                                     consumer_secret=self._consumer_secret,
                                     access_token_key=self._access_token_key,
                                     access_token_secret=self._access_token_secret,)
        self.is_authenticated = True

    @wrap_exceptions
    def get_home_timeline(self):
        return self._api.get_home_timeline()

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
        args = status,
        favorite_thread = Thread(target=self._api.create_favorite, args=args)
        favorite_thread.start()

    @wrap_exceptions
    def destroy_favorite(self, status):
        args = status,
        unfavorite_thread = Thread(target=self._api.destroy_favorite, args=args)
        unfavorite_thread.start()
