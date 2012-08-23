# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest
from functools import partial

from turses.session import Session
from turses.models import Timeline, TimelineList
from turses.api.debug import MockApi


def check_update_function_name(timeline, update_function_name=None):
    if not isinstance(timeline, Timeline):
        return False

    update_function = timeline.update_function
    if update_function is None:
        return False

    return update_function.__name__ == update_function_name

is_home_timeline = partial(check_update_function_name,
                           update_function_name='get_home_timeline')
is_mentions_timeline = partial(check_update_function_name,
                               update_function_name='get_mentions')
is_favorites_timeline = partial(check_update_function_name,
                               update_function_name='get_favorites')
is_own_timeline = partial(check_update_function_name,
                          update_function_name='get_own_timeline')
is_messages_timeline = partial(check_update_function_name,
                               update_function_name='get_direct_messages')


class HelperFunctionTest(unittest.TestCase):
    def setUp(self):
        self.api = MockApi('foo', 'bar')

    def test_is_home_timeline(self):
        a_timeline = Timeline()
        assert not is_home_timeline(a_timeline)

        home_timeline = Timeline(update_function=self.api.get_home_timeline)
        assert is_home_timeline(home_timeline)

    def test_is_mentions_timeline(self):
        a_timeline = Timeline()
        assert not is_mentions_timeline(a_timeline)

        mentions_timeline = Timeline(update_function=self.api.get_mentions)
        assert is_mentions_timeline(mentions_timeline)

    def test_is_favorites_timeline(self):
        a_timeline = Timeline()
        assert not is_favorites_timeline(a_timeline)

        favorites_timeline = Timeline(update_function=self.api.get_favorites)
        assert is_favorites_timeline(favorites_timeline)

    def test_is_own_timeline(self):
        a_timeline = Timeline()
        assert not is_own_timeline(a_timeline)

        own_timeline = Timeline(update_function=self.api.get_own_timeline)
        assert is_own_timeline(own_timeline)

    def test_is_messages_timeline(self):
        a_timeline = Timeline()
        assert not is_messages_timeline(a_timeline)

        messages_timeline = Timeline(update_function=self.api.get_direct_messages)
        assert is_messages_timeline(messages_timeline)


class SessionTest(unittest.TestCase):
    def test_default_session_timelines(self):
        """
        Test that, by default, the following timelines are loaded: `home`,
        `mentions`, `favorites`, `messages` and `own_tweets`.
        """
        timeline_list = TimelineList()
        session = Session(MockApi('foo', 'bar'))
        session.populate(timeline_list)

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
        session = Session(MockApi('foo', 'bar'))
        session.populate(timeline_list)

        self.assertEqual(timeline_list.visible_timelines, [timeline_list[0]])
