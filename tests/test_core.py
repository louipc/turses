# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from mock import Mock

from . import create_status
from turses.models import TimelineList
from turses.api.helpers import (
    is_home_timeline,
    is_user_timeline,
    is_own_timeline,
    is_mentions_timeline,
    is_messages_timeline,
    is_thread_timeline,
)
from turses.config import configuration
from turses.core import InputHandler, Controller
from turses.api.debug import MockApi


class InputHandlerTest(unittest.TestCase):

    # - Helpers ---------------------------------------------------------------

    def executes(self, commands):
        """Assert that calling the key handlers `handle` method with all
        the keys corresponding to the commands in `commands` calls the
        handler for that command."""
        for command in commands:
            handler = commands[command]
            key = self.key(command)

            self.key_handler.handle(key)

            self.failUnless(handler.called)

    def does_not_execute(self, commands):
        """Assert that calling the key handlers `handle` method with all
        the keys corresponding to the commands in `commands` DOES NOT call the
        handler for that command."""
        for command in commands:
            handler = commands[command]
            key = self.key(command)

            self.key_handler.handle(key)

            self.failIf(handler.called)

    def key(self, command):
        key, _ = configuration.key_bindings[command]
        return key

    # - Tests -----------------------------------------------------------------

    def setUp(self):
        self.controller = Mock(Controller)
        self.key_handler = InputHandler(self.controller)

        return_false = Mock(return_value=False)
        self.controller.is_in_info_mode = return_false
        self.controller.is_in_timeline_mode = return_false
        self.controller.is_in_help_mode = return_false
        self.controller.is_in_user_info_mode = return_false
        self.controller.is_in_editor_mode = return_false

    def test_info_mode(self):
        self.controller.is_in_info_mode = Mock(return_value=True)

        # execute
        self.executes(self.key_handler.TURSES_COMMANDS)
        self.executes(self.key_handler.TIMELINE_COMMANDS)

        # don't execute
        self.does_not_execute(self.key_handler.MOTION_COMMANDS)
        self.does_not_execute(self.key_handler.BUFFER_COMMANDS)
        self.does_not_execute(self.key_handler.TWITTER_COMMANDS)
        self.does_not_execute(self.key_handler.EXTERNAL_PROGRAM_COMMANDS)

    def test_timeline_mode(self):
        self.controller.is_in_timeline_mode = Mock(return_value=True)

        self.executes(self.key_handler.TURSES_COMMANDS)
        self.executes(self.key_handler.MOTION_COMMANDS)
        self.executes(self.key_handler.BUFFER_COMMANDS)
        self.executes(self.key_handler.TIMELINE_COMMANDS)
        self.executes(self.key_handler.TWITTER_COMMANDS)
        self.executes(self.key_handler.EXTERNAL_PROGRAM_COMMANDS)

    def test_help_mode(self):
        self.controller.is_in_help_mode = Mock(return_value=True)

        # execute
        self.executes(self.key_handler.TURSES_COMMANDS)
        self.executes(self.key_handler.MOTION_COMMANDS)

        # don't execute
        self.does_not_execute(self.key_handler.TIMELINE_COMMANDS)
        self.does_not_execute(self.key_handler.BUFFER_COMMANDS)
        self.does_not_execute(self.key_handler.TWITTER_COMMANDS)
        self.does_not_execute(self.key_handler.EXTERNAL_PROGRAM_COMMANDS)

    def test_editor_mode(self):
        self.controller.is_in_editor_mode = Mock(return_value=True)

        self.does_not_execute(self.key_handler.TURSES_COMMANDS)
        self.does_not_execute(self.key_handler.MOTION_COMMANDS)
        self.does_not_execute(self.key_handler.TIMELINE_COMMANDS)
        self.does_not_execute(self.key_handler.BUFFER_COMMANDS)
        self.does_not_execute(self.key_handler.TWITTER_COMMANDS)
        self.does_not_execute(self.key_handler.EXTERNAL_PROGRAM_COMMANDS)

        for key in "ABCDEFGHIJKLMNÑOPQRSTUVWXYZabcdefghijklmnñopqrstuvwxyz":
            self.key_handler.handle(key)
            self.controller.forward_to_editor.assert_called_with(key)


class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.timelines = TimelineList()
        self.controller = Controller(ui=Mock(),
                                api=MockApi('foo', 'bar'),
                                timelines=self.timelines)

    def test_append_home_timeline(self):
        self.controller.append_home_timeline()

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_home_timeline(appended_timeline))

    def test_append_user_timeline(self):
        user = 'dialelo'
        self.controller.append_user_timeline(user)

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_user_timeline(appended_timeline))
        self.assertEqual(appended_timeline._kwargs, {'screen_name': user})

    def test_own_tweets_timeline(self):
        self.controller.append_own_tweets_timeline()

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_own_timeline(appended_timeline))

    def test_mentions_timeline(self):
        self.controller.append_mentions_timeline()

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_mentions_timeline(appended_timeline))

    def test_direct_messages_timeline(self):
        self.controller.append_direct_messages_timeline()

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_messages_timeline(appended_timeline))

    def test_thread_timeline(self):
        active_timeline = self.controller.timelines.active
        active_timeline.add_status(create_status())
        # make sure that there is at least one status in the active timeline
        self.assertTrue(active_timeline.active)

        self.controller.append_thread_timeline()

        appended_timeline = self.timelines[-1]
        self.assertTrue(is_thread_timeline(appended_timeline))

    # TODO: test `append_search_timeline`
    # TODO: test `append_retweets_of_me_timeline`


if __name__ == '__main__':
    unittest.main()
