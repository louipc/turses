# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from . import create_status, create_direct_message

from turses.models import Timeline
from turses.api.base import AsyncApi
from turses.api.debug import MockApi
from turses.api.backends import TweepyApi
from turses.api.helpers import (
    TimelineFactory,

    is_home_timeline,
    is_mentions_timeline,
    is_favorites_timeline,
    is_messages_timeline,
    is_own_timeline,
    is_search_timeline,
    is_user_timeline,
    is_retweets_of_me_timeline,
    is_thread_timeline,
)


ACCESS_TOKEN = 'Yohohohoooo'
ACCESS_TOKEN_SECRET = 'Skull joke!'

mock_api = MockApi(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


class AsyncApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         AsyncApi(MockApi,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET,)


class MockApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         MockApi(access_token_key=ACCESS_TOKEN,
                 access_token_secret=ACCESS_TOKEN_SECRET,)


class TweepyApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         TweepyApi(access_token_key=ACCESS_TOKEN,
                   access_token_secret=ACCESS_TOKEN_SECRET,)


class HelperFunctionTest(unittest.TestCase):
    def test_is_home_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_home_timeline(a_timeline))

        home_timeline = Timeline(update_function=mock_api.get_home_timeline)
        self.assertTrue(is_home_timeline(home_timeline))

    def test_is_mentions_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_mentions_timeline(a_timeline))

        mentions_timeline = Timeline(update_function=mock_api.get_mentions)
        self.assertTrue(is_mentions_timeline(mentions_timeline))

    def test_is_favorites_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_favorites_timeline(a_timeline))

        favorites_timeline = Timeline(update_function=mock_api.get_favorites)
        self.assertTrue(is_favorites_timeline(favorites_timeline))

    def test_is_own_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_own_timeline(a_timeline))

        own_timeline = Timeline(update_function=mock_api.get_own_timeline)
        self.assertTrue(is_own_timeline(own_timeline))

    def test_is_messages_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_messages_timeline(a_timeline))

        messages_timeline = Timeline(update_function=mock_api.get_direct_messages)
        self.assertTrue(is_messages_timeline(messages_timeline))

    def test_is_search_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_search_timeline(a_timeline))

        search_timeline = Timeline(update_function=mock_api.search)
        self.assertTrue(is_search_timeline(search_timeline))

    def test_is_user_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_user_timeline(a_timeline))

        user_timeline = Timeline(update_function=mock_api.get_user_timeline)
        self.assertTrue(is_user_timeline(user_timeline))

    def test_is_retweets_of_me_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_retweets_of_me_timeline(a_timeline))

        rts_timeline = Timeline(update_function=mock_api.get_retweets_of_me)
        self.assertTrue(is_retweets_of_me_timeline(rts_timeline))

    def test_is_thread_timeline(self):
        a_timeline = Timeline()
        self.assertFalse(is_thread_timeline(a_timeline))

        thread_timeline = Timeline(update_function=mock_api.get_thread)
        self.assertTrue(is_thread_timeline(thread_timeline))


class TimelineFactoryTest(unittest.TestCase):
    def setUp(self):
        self.factory = TimelineFactory(mock_api)

    def valid_name(self, timeline_name):
        """Test that `timeline_name` is a valid timeline name."""
        self.assertTrue(self.factory.valid_timeline_name(timeline_name))

    def test_default_names_are_valid_timeline_names(self):
        self.valid_name('home')
        self.valid_name('mentions')
        self.valid_name('favorites')
        self.valid_name('messages')
        self.valid_name('own_tweets')

    def test_search_names_are_valid_timeline_name(self):
        self.valid_name('search:turses')
        self.valid_name('search:I love ramen!')
        self.valid_name('search:#Python is awesome')

    def test_user_names_are_valid_timeline_name(self):
        self.valid_name('user:dialelo')
        self.valid_name('user:PepeGuer')

    def test_retweets_of_me_is_valid_timeline_name(self):
        self.valid_name('retweets_of_me')

    def created_timeline_verifies(self, name, prop):
        """
        Test that the timeline created from `name` verifies the `prop`
        property.
        """
        timeline = self.factory(name)
        self.assertTrue(prop(timeline))

    # TODO: remove hardcoded timeline names
    def test_timeline_factory_home(self):
        self.created_timeline_verifies('home', is_home_timeline)

    def test_timeline_factory_mentions(self):
        self.created_timeline_verifies('mentions', is_mentions_timeline)

    def test_timeline_factory_favorites(self):
        self.created_timeline_verifies('favorites', is_favorites_timeline)

    def test_timeline_factory_messages(self):
        self.created_timeline_verifies('messages', is_messages_timeline)

    def test_timeline_factory_own_tweets(self):
        self.created_timeline_verifies('own_tweets', is_own_timeline)

    def test_timeline_factory_search(self):
        self.created_timeline_verifies('search:turses', is_search_timeline)

    def test_timeline_factory_search_query(self):
        query = 'Programming is fun'

        timeline = self.factory(':'.join(['search', query]))

        self.assertEqual(timeline._args, [query])

    def test_timeline_factory_retweets_of_me(self):
        self.created_timeline_verifies('retweets_of_me',
                                       is_retweets_of_me_timeline)

    def test_thread(self):
        status = create_status()

        thread_timeline = self.factory.thread(status)

        self.assertEqual(thread_timeline.update_function.__name__,
                         'get_thread',)
        self.assertEqual(thread_timeline._args[0], status)

    def test_dm_thread(self):
        message = create_direct_message()

        dm_thread_timeline = self.factory.thread(message)

        self.assertEqual(dm_thread_timeline.update_function.__name__,
                         'get_message_thread',)
        self.assertEqual(dm_thread_timeline._args[0], message)
