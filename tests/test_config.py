# -*- coding: utf-8 -*-

import unittest
from mock import Mock
from os.path import join
from sys import path
path.append('../')

from turses.config import (
        PALETTE,

        CONFIG_PATH,
        DEFAULT_CONFIG_FILE,
        DEFAULT_TOKEN_FILE,

        validate_color,
        Configuration,
)


class Args(object):
    """
    Represents the arguments.
    """
    def __init__(self,
                 account=None,
                 config=None,
                 generate_config=None):
        self.account = account
        self.config = config
        self.generate_config = generate_config


class ConfigurationTest(unittest.TestCase):
    """Tests for `turses.config.Configuration`."""

    def test_palette(self):
        """Test that every color in the default `PALETTE` is valid."""
        for label in list(PALETTE):
            # ignore the label name
            for color in label[1:]:
                if color:
                    self.assertTrue(validate_color(color))

    def test_defaults(self):
        """Test that defaults get loaded correctly."""
        config = Configuration()
        self.assertEqual(config.config_file, DEFAULT_CONFIG_FILE)
        self.assertEqual(config.token_file, DEFAULT_TOKEN_FILE)

    def test_parse_config_file(self):
        pass

    def test_parse_token_file(self):
        pass

    def test_parse_legacy_config_file(self):
        pass

    def test_parse_legacy_token_file(self):
        pass

    def test_set_color(self):
        """Test `Configuration._set_color`."""
        config = Configuration()

        palette = [
            ['first', 'cyan', 'black', 'default', ''],
            ['second', 'green', 'black']
        ]
        modified_color = ['first', 'black', 'cyan', 'default', '']
        palette[0] = modified_color
        label, fg, bg = modified_color[:3]

        config.palette = list(palette)
        config._set_color(label, fg, bg)

        self.assertEqual(palette, config.palette)

        config._set_color('idontexist', fg, bg)
        self.assertEqual(palette, config.palette)

    def test_set_key_binding(self):
        """Test `Configuration._set_key_binding`."""
        config = Configuration()

        key_bindings = {
            'quit': ('q', 'Quit the program'),
            'help': ('h', 'Show help')
        }

        config.key_bindings = key_bindings.copy()
        # swap the key bindings
        config._set_key_binding('quit', 'h')
        config._set_key_binding('help', 'q')
        swapped_key_bindings = {
            'quit': ('h', 'Quit the program'),
            'help': ('q', 'Show help')
        }

        self.assertEqual(swapped_key_bindings, config.key_bindings)

        config._set_key_binding('idontexist', '~')
        self.assertEqual(swapped_key_bindings, config.key_bindings)

    def test_args_account(self):
        account = 'bob'
        args = Args(account=account)
        config = Configuration(args)
        token_path = join(CONFIG_PATH, "%s.token" % account)
        self.assertEqual(token_path, config.token_file)

    def test_args_generate_config(self):
        config_path = '~/.turses/custom_config'
        args = Args(generate_config=config_path)
        ConfigurationMock = Mock(Configuration)
        config = ConfigurationMock(args)
        config.generate_config_file.assert_called_once()

    def test_args_config(self):
        config_path = '/path/to/custom/config/file'
        args = Args(config=config_path)
        config = Configuration(args)
        self.assertEqual(config_path, config.config_file)


if __name__ == '__main__':
    unittest.main()
