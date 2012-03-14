###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import os
import sys
import urllib2
import oauth2 as oauth

from twitter import Api as BaseApi 
from twitter import TwitterError, Status, _FileCache

try:
    import json
except ImportError:
    pass  
    #import simplejson as json

DEFAULT_CACHE = object()

class Api(BaseApi):
    """Subclass of `python-twitter` library's `Api` class."""
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


# TODO document every method and give it arguments according to the API methods
class ApiAdapter(object):
    """
    An adapter for the different libraries that implement the Twitter's API.
    """

    # TODO: implement every action in the Twitter's API:
    #           http://dev.twitter.com/docs/api

    # Timelines

    def get_home_timeline(self):
        pass

    def get_mentions(self):
        pass

    def get_own_favorites(self):
        pass

    def get_retweeted_by_me(self):
        pass

    def get_retweeted_to_me(self):
        pass

    def get_retweets_of_me(self):
        pass

    def get_user_timeline(self, username=None):
        pass

    def get_own_tweets(self):
        return self.get_user_timeline()

    def get_retweeted_to_user(self, username):
        pass

    def get_retweeted_by_user(self, username):
        pass

    # Tweets

    def get_retweeted_by(self, status):
        """Returns a list with the users that retweeted `status`."""
        pass

    def get_retweeted_by_ids(self, status):
        """Returns a list of IDs of the users that retweeted `status`."""
        pass

    def get_retweets(self, status):
        """Returns up to 100 of the first retweets of `status`."""
        pass

    def get_status_by_id(self, id):
        """Returns a single status, specified by the `id` parameter."""
        pass

    def destroy(self, status):
        """
        Destroy the given `status`. The authenticated user must be the 
        author of the specified status.
        """
        pass

    def retweet(self, status):
        """Retweets the given `status`."""
        pass

    def update(self, text):
        """Updates the authenticating user's status."""
        pass

    def update_with_media(self, text):
        """
        Updates the authenticating user's status and attaches media for upload.
        """
        pass

    # Search

    def search(self, text):
        """Returns tweets that match the specified `text`."""
        pass

    # Direct Messages

    def get_direct_messages(self):
        """
        Return the 20 most recent direct messages sent to the authenticating
        user.
        """
        pass

    def get_sent_direct_messages(self):
        """
        Return the 20 most recent direct messages sent by the authenticating
        user.
        """
        pass

    def destroy_direct_message(self, dm):
        """Deletes the given `dm`."""
        pass

    def direct_message(self, username, text):
        """
        Sends a new direct message to the specified user from the authenticating 
        user.
        """
        pass

    def get_direct_message_by_id(self, id):
        """Returns a single direct message, specified by the `id` parameter."""
        pass

    # Friends & Followers

    def get_followers_ids(self, username):
        """Returns a list of IDs for every user following the specified user."""
        pass

    def get_friends_ids(self, username):
        """
        Returns a list of IDs for every user the specified user is following.
        """
        pass

    def friendship_exists(self, a_user, another_user):
        """
        Returns `True` if the user `a_user` follows the `another_user`.
        """
        pass

    def get_incoming_friendship(self):
        """
        Returns a list of IDs for every user who has a pending request to
        follow the authenticating user.
        """
        pass

    def get_outgoing_friendship(self):
        """
        Returns a list of IDs for every protected user for whom the 
        authenticating user has a pending request.
        """
        pass

    def get_friendship(self, a_user, another_user):
        """
        Returns detailed information about the friendship between `a_user`
        and `another_user`.
        """
        pass

    def create_friendship(self, user_id):
        """
        Allows the authenticating user to follow the user ID specified in the 
        `user_id` parameter. 
        """
        pass

    def destroy_friendship(self, user_id):
        """
        Allows the authenticating user to unfollow the user ID specified in the 
        `user_id` parameter. 
        """
        pass

    def lookup_friendship(self, users):
        """
        Returns the relationship of the authenticating user to the specified 
        list of users.
        """
        pass

    def update_friendship(self, user):
        """
        Allows one to enable or disable retweets and device notifications 
        from the specified `user`.
        """
        pass

    def get_no_retweets_ids(self):
        """
        Returns an array of user_IDs that the currently authenticated user does 
        not want to see retweets from.
        """
        pass

    # Users

    def lookup_users(self, users):
        """
        Return information about the given `users` with their most recent
        status (if the authenticated user has permission).
        """
        pass

    def get_profile_image(self, username):
        """
        Return the profile image for the user with the indicated `username`.
        """
        pass

    def search_users(self, text):
        """
        Search for `text` in Twitter usernames.
        """
        pass

    def get_user(self, username):
        """
        Returns information about the user with the given `username` and the
        user's most recent status.
        """
        pass

    def get_user_contributees(self, username):
        """
        Returns an array of users that the specified user can contribute to.
        """
        pass

    def get_user_contributors(self, username):
        """
        Returns an array of users who can contribute to the specified user.
        """
        pass

    # Suggested users

    def get_user_category_suggestions(self):
        """Returns a list of suggested user categories."""
        pass

    def get_user_suggestions(self, category):
        """
        Access the users in the given `category` of the Twitter suggested user 
        list.
        """
        pass

    def get_user_suggestions_with_status(self, category):
        """
        Access the users in the given `category` of the Twitter suggested user 
        list with their most recent status.
        """
        pass

    # Favorites

    def get_favorites(self, user_id):
        """
        Returns the 20 most recent favorite statuses for the authenticating user 
        or user specified by the ID parameter.
        """
        pass

    def create_favorite(self, status):
        """
        Favorites `status` as the authenticating user.
        """
        pass

    def destroy_favorite(self, status):
        """
        Un-favorites `status` as the authenticating user.
        """
        pass

    # Lists

    def get_own_subscribed_lists(self):
        """
        Returns all lists the authenticating subscribes to, including their own.
        """
        pass

    def get_subscribed_lists(self, user):
        """
        Returns all lists the specified user subscribes to, including their own.
        """
        pass

    def get_list_statuses(self, list):
        """
        Returns tweet timeline for members of the specified list.
        """
        pass

    def remove_user_from_list(self, user, list):
        """
        Removes the specified `user` from the `list`. The authenticated user must 
        be the list's owner to remove members from the list.
        """
        pass

    def get_list_memberships(self, user):
        """
        Returns the lists the specified user has been added to.
        """
        pass

    def get_own_list_memberships(self):
        """
        Returns the lists the authenticating user has been added to.
        """
        pass

    def get_list_subscribers(self, list):
        """
        Returns the subscribers of the specified list. Private list subscribers 
        will only be shown if the authenticated user owns the specified list.
        """
        pass

    def create_list_subscription(self, list):
        """
        Subscribes the authenticated user to the specified list.
        """
        pass

    def is_subscrided_to_list(self, user, list):
        """
        Check if the specified `user` is a subscriber of the specified `list`. 
        """
        pass

    def destroy_list_subscription(self, list):
        """
        Unsubscribes the authenticated `user` from the specified `list`.
        """
        pass

    def add_members_to_list(self, users, list):
        """
        Adds specified `users` to `list`. The authenticated user must own the 
        list to be able to add members to it.
        """
        pass

    def is_member_of_list(self, user, list):
        """
        Check if the specified `user` is a member of the specified `list`.
        """
        pass

    def get_list_members(self, list):
        """
        Returns the members of the specified `list`. Private list members will 
        only be shown if the authenticated user owns the specified list.
        """
        pass

    def add_member_to_list(self, user, list):
        """
        Add `user` to `list`. The authenticated user must own the list to be 
        able to add members to it.
        """
        pass

    def destroy_list(self, list):
        """
        Deletes the specified `list`. The authenticated user must own the list 
        to be able to destroy it.
        """
        pass

    def update_list(self, list):
        """
        Updates the specified `list`. The authenticated user must own the list 
        to be able to update it.
        """
        pass

    def create_list(self, list):
        """
        Creates a new list for the authenticated user.
        """
        pass

    def get_lists(self, user):
        """
        Returns the lists of the specified `user`. Private lists will be included 
        if the authenticated user is the same as the user whose lists are 
        being returned.
        """
        pass

    def get_own_lists(self):
        """
        Returns the lists of the authenticated user.
        """
        pass

    def get_list(self, list):
        """
        Returns the specified `list`. Private lists will only be shown if 
        the authenticated user owns the specified list.
        """
        pass

    def get_user_subscriptions(self, user):
        """
        Obtain a collection of the lists the specified `user` is subscribed to, 
        does not include the user's own lists.
        """
        pass

    # Accounts

    def get_rate_limit_status(self):
        """
        Returns the remaining number of API requests available to the requesting 
        user before the API limit is reached for the current hour. 
        """
        pass

    def verify_credential(self):
        """
        Returns a representation of the requesting user if authentication 
        was successful.
        """
        pass

    def end_session(self):
        """
        Ends the session of the authenticating user.
        """
        pass

    def update_profile(self, **kwargs):
        """
        Sets values that users are able to set under the "Account" tab of 
        their settings page.
        """
        pass

    def update_profile_background_image(self, image):
        """Updates the authenticating user's profile background image."""
        pass

    def update_profile_colors(self, colors):
        """
        Sets one or more hex values that control the color scheme of the 
        authenticating user's profile page on twitter.com. 
        
        Each parameter's value must be a valid hexidecimal value, and may be 
        either three or six characters (ex: #fff or #ffffff).
        """
        pass
    
    def update_profile_image(self, image):
        """Updates the authenticating user's profile image."""
        pass

    def get_totals(self):
        """
        Returns the current count of friends, followers, updates (statuses) and 
        favorites of the authenticating user.
        """
        pass

    def get_settings(self):
        """
        Returns settings (including current trend, geo and sleep time information) 
        for the authenticating user.
        """
        pass

    def set_settings(self, settings):
        """
        Updates the authenticated user's settings.
        """
        pass

    # Notification
    #  SMS-based notifications

    def notifications_follow(self, user):
        """Enables device notifications for updates from the specified `user`."""
        pass

    def notifications_leave(self, user):
        """Disables device notifications for updates from the specified `user`."""
        pass

    # Saved Searches

    def get_saved_searches(self):
        """Returns the authenticated user's saved search queries."""
        pass

    def get_saved_search_by_id(self, id):
        """
        Retrieve the information for the saved search represented by the given 
        `id`. The authenticating user must be the owner of saved search ID 
        being requested."""
        pass

    def create_saved_search(self):
        """Create a new saved search for the authenticated user."""
        pass

    def destroy_saved_search(self, id):
        """  
        Destroys a saved search for the authenticating user. The authenticating 
        user must be the owner of saved search `id` being destroyed.
        """
        pass

    # Places & Geo

    def get_place(self, id):
        """Returns all the information about a known place."""
        pass

    def reverse_geocode(self, latitude, longitude):
        """
        Given a latitude and a longitude, searches for places that can be used 
        as a place_id when updating a status.
        """
        pass

    def search_place(self, latitude=None, longitude=None, ip=None, name=None):
        """
        Search for places that can be attached to a statuses/update. 
        
        Given a latitude and a longitude pair, an IP address, or a name, this 
        method will return a list of all the valid places that can be used as the 
        place_id when updating a status.
        """
        pass

    def get_similar_places(self, latitude, longitude):
        """
        Locates places near the given coordinates which are similar in name.
        """
        pass

    def create_place(self, latitude, longitude):
        """
        Creates a new place object at the given latitude and longitude.
        """
        pass

    # Trends 

    def get_trends(self, woeid):
        pass

    def get_trends_available_locations(self):
        pass

    def get_daily_trends(self):
        pass

    def get_weekly_trends(self):
        pass

    # Block

    def get_blocking(self):
        pass

    def get_blocking_ids(self):
        pass

    def is_blocking(self, user):
        pass

    def block(self, user):
        pass

    def unblock(self, user):
        pass

    # Spam

    def report_spam(self, user):
        pass

    # Oauth

    def oauth_authenticate(self):
        pass

    def oauth_authorize(self):
        pass

    def oauth_acces_token(self):
        pass

    def oauth_request_token(self):
        pass

    # Help

    def help_test(self):
        pass

    def help_configuration(self):
        pass

    def help_languages(self):
        pass

    # Legal

    def get_privacy_policy(self):
        pass

    def get_terms_of_service(self):
        pass
