# -*- coding: utf-8 -*-

"""
turses.api.backends
~~~~~~~~~~~~~~~~~~~

This module contains implementations of `turses.api.base.Api` using multiple
API backends.
"""

from tweepy import API as BaseTweepyApi
from tweepy import OAuthHandler as TweepyOAuthHandler

from turses.models import (
        User,
        Status,
        DirectMessage,
        List,

        get_authors_username,
        get_mentioned_usernames,
)
from turses.utils import datetime_from_twitter_datestring
from turses.api.base import Api


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
            text = status.text

            is_reply = False
            in_reply_to_user = ''
            is_retweet = False
            retweet_count = 0
            is_favorite = False
            author = ''

            if getattr(status, 'retweeted_status', False):
                is_retweet = True
                text = status.retweeted_status.text
                retweet_count = status.retweet_count
                author = status.retweeted_status.author.screen_name

            if status.in_reply_to_screen_name:
                is_reply = True
                in_reply_to_user = status.in_reply_to_screen_name

            if status.favorited:
                is_favorite = True

            kwargs = {
                'id': status.id,
                'created_at': status.created_at,
                'user': status.user.screen_name,
                'text': text,
                'is_retweet': is_retweet,
                'is_reply': is_reply,
                'is_favorite': is_favorite,
                'in_reply_to_user': in_reply_to_user,
                'retweet_count': retweet_count,
                'author': author,
            }
            return Status(**kwargs)

        if isinstance(statuses, list):
            return [to_status(status) for status in statuses]
        else:
            return to_status(statuses)

    def _to_direct_message(self, dms):
        def to_direct_message(dm):
            kwargs = {
                'id': dm.id,
                'created_at': dm.created_at,
                'sender_screen_name': dm.sender_screen_name,
                'recipient_screen_name': dm.recipient_screen_name,
                'text': dm.text,
            }
            return DirectMessage(**kwargs)

        if isinstance(dms, list):
            return [to_direct_message(dm) for dm in dms]
        else:
            return to_direct_message(dms)

    def _to_list(self, lists):
        def to_list(l):
            created_at = datetime_from_twitter_datestring(l.created_at)
            if l.mode == u'private':
                private = True
            else:
                private = False

            kwargs = {
                'id': l.id,
                'owner': l.user.screen_name,
                'created_at': created_at,
                'name': l.name,
                'description': l.description,
                'member_count': l.member_count,
                'subscriber_count': l.subscriber_count,
                'private': private,
            }
            return List(**kwargs)

        if isinstance(lists, list):
            return [to_list(l) for l in lists]
        else:
            return to_list(lists)

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

    # timelines

    def get_home_timeline(self, **kwargs):
        tweets = self._api.home_timeline(**kwargs)
        retweets = self._api.retweeted_to_me(**kwargs)
        tweets.extend(retweets)
        return self._to_status(tweets)

    def get_user_timeline(self, screen_name, **kwargs):
        return self._to_status(self._api.user_timeline(screen_name,
                                                       **kwargs))

    def get_own_timeline(self, **kwargs):
        me = self.verify_credentials()
        tweets = self._api.user_timeline(screen_name=me.screen_name,
                                         **kwargs)
        retweets = self._api.retweeted_by_me(**kwargs)
        tweets.extend(retweets)
        return self._to_status(tweets)

    def get_mentions(self, **kwargs):
        return self._to_status(self._api.mentions(**kwargs))

    def get_favorites(self, **kwargs):
        return self._to_status(self._api.favorites(**kwargs))

    def get_direct_messages(self, **kwargs):
        dms = self._api.direct_messages(**kwargs)
        sent = self._api.sent_direct_messages(**kwargs)
        dms.extend(sent)
        return self._to_direct_message(dms)

    def get_thread(self, status, **kwargs):
        author = get_authors_username(status)
        mentioned = get_mentioned_usernames(status)
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

    def get_search(self, text, **kwargs):
        # `tweepy.API.search` returns `tweepy.models.SearchResult` objects instead
        # `tweepy.models.Status` so we have to convert them differently
        def to_status(status):
            kwargs = {
                'id': status.id,
                'created_at': status.created_at,
                'user': status.from_user,
                'text': status.text,
            }
            return Status(**kwargs)

        results = self._api.search(text, **kwargs)
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
