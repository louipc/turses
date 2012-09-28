# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from . import create_status, create_direct_message

from turses.api.debug import MockApi
from turses.models import Timeline, TimelineList
from turses.session import (
    Session,
    TimelineFactory,

    clean_timeline_list_string,
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


mock_api = MockApi('foo', 'bar')


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

    def test_clean_timeline_list_string(self):
        self.assertEqual(clean_timeline_list_string(''), [])

        self.assertEqual(clean_timeline_list_string('  '), [])

        self.assertEqual(clean_timeline_list_string('home'), ['home'])

        self.assertEqual(clean_timeline_list_string('  home, '), ['home'])

        self.assertEqual(clean_timeline_list_string('home, mentions'),
                         ['home', 'mentions'])

        self.assertEqual(clean_timeline_list_string('  home,mentions '),
                         ['home', 'mentions'])

        self.assertEqual(clean_timeline_list_string('mentions, favorites, messages, own_tweets'),
                         ['mentions', 'favorites', 'messages', 'own_tweets'])


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


class SessionTest(unittest.TestCase):
    def setUp(self):
        self.session = Session(mock_api)

    def test_default_session_timelines(self):
        """
        Test that, by default, the following timelines are loaded: `home`,
        `mentions`, `favorites`, `messages` and `own_tweets`.
        """
        timeline_list = TimelineList()
        self.session.populate(timeline_list)

        self.assertTrue(is_home_timeline(timeline_list[0]))
        self.assertTrue(is_mentions_timeline(timeline_list[1]))
        self.assertTrue(is_favorites_timeline(timeline_list[2]))
        self.assertTrue(is_messages_timeline(timeline_list[3]))
        self.assertTrue(is_own_timeline(timeline_list[4]))

    def test_default_session_only_visible_first_timeline(self):
        """
        Test that, by default, only the `home` timeline is visible.
        """
        timeline_list = TimelineList()
        self.session.populate(timeline_list)

        self.assertEqual(timeline_list.visible_timelines, [timeline_list[0]])

    def test_custom_session(self):
        """
        Test that, when defining a custom session, the timelines are created
        correctly.
        """
        timeline_list = TimelineList()

        visible_string = 'home, mentions, search:turses'
        self.session.append_visible_timelines(visible_string, timeline_list)

        # check that the visible timelines are appended correctly
        self.assertTrue(len(timeline_list), 3)

        self.assertTrue(is_home_timeline(timeline_list[0]))
        self.assertTrue(is_mentions_timeline(timeline_list[1]))
        self.assertTrue(is_search_timeline(timeline_list[2]))

        self.assertEqual(timeline_list.visible_timelines,
                         [timeline_list[0], timeline_list[1], timeline_list[2]])

        # now let's append the buffers in the background
        buffers_string = 'messages'
        self.session.append_background_timelines(buffers_string, timeline_list)

        self.assertTrue(len(timeline_list), 4)

        self.assertTrue(is_messages_timeline(timeline_list[3]))
