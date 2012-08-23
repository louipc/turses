# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

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

    def created_timeline_verifies(self, name, prop):
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

        visible_string = 'home, mentions'
        self.session.append_visible_timelines(visible_string, timeline_list)

        # check that the visible timelines are appended correctly
        self.assertTrue(len(timeline_list), 2)

        self.assertTrue(is_home_timeline(timeline_list[0]))
        self.assertTrue(is_mentions_timeline(timeline_list[1]))

        self.assertEqual(timeline_list.visible_timelines,
                         [timeline_list[0], timeline_list[1]])

        # now let's append the buffers in the background
        buffers_string = 'messages'
        self.session.append_background_timelines(buffers_string, timeline_list)

        self.assertTrue(len(timeline_list), 3)

        self.assertTrue(is_messages_timeline(timeline_list[2]))
