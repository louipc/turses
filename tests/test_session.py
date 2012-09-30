# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from . import create_status, create_direct_message

from turses.api.debug import MockApi
from turses.models import Timeline, TimelineList
from turses.session import (
    Session,

    clean_timeline_list_string,
)
from turses.api.helpers import (
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



class SessionTest(unittest.TestCase):
    def setUp(self):
        self.session = Session(mock_api)

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
