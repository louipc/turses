# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from mock import Mock

from turses.config import configuration
from turses.core import KeyHandler, Controller


class KeyHandlerTest(unittest.TestCase):

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
        self.key_handler = KeyHandler(self.controller)

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


if __name__ == '__main__':
    unittest.main()
