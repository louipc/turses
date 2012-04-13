# -*- coding: utf-8 -*-

"""
turses.config
~~~~~~~~~~~~~

This module contains the configuration logic.


There is one mayor configuration file in turses:

    `config`
        contains user preferences: colors, bindings, etc.

And each user account has its .token file with authentication tokens.
Keep this secret.

    `<username>.token`
        contains the oauth tokens

The standar location is under $HOME directory, in a folder called `.turses`.
Here is an example with two user accounts: `alice` and `bob`.

    ~
    |+.turses/
    | |-config
    | |-alice.token
    | `-bob.token
    |+...
    |-...
    `
"""

from ConfigParser import RawConfigParser
from os import environ, path, mkdir
from gettext import gettext as _

from . import defaults
from .utils import encode
from .api.base import authorization


HOME = environ['HOME']
BROWSER = environ['BROWSER']

CONFIG_DIR = '.turses'
CONFIG_PATH = path.join(HOME, CONFIG_DIR)

class Configuration(object):
    """
    Create and parse configuration files.

    Has backwards compatibility with the Tyrs legacy configuration.
    """
    SECTION_KEY_BINDINGS = 'bindings'
    SECTION_PALETTE = 'palette'
    SECTION_STYLES = 'styles'
    SECTION_DEBUG = 'debug'

    def __init__(self, cli_args):
        """
        Create a `Configuration` object taking into account the arguments
        provided in the command line interface.
        """
        self.load_defaults()

        # create the config directory if it does not exist
        if not path.isdir(CONFIG_PATH):
            try:
                mkdir(CONFIG_PATH)
            except:
                print encode(_('Error creating config directory in %s' % CONFIG_DIR))

        # generate config file and exit
        if cli_args.generate_config:
            self.generate_config_file(cli_args.generate_config)
            exit(0)

        if cli_args.config:
            config_file = cli_args.config
        else:
            config_file = path.join(CONFIG_PATH, 'config')
        self._init_config(config_file)

        if cli_args.account:
            token_file = path.join(CONFIG_PATH, '%s.token' % cli_args.account)
        else:
            # loads the default `token' if no account was specified 
            token_file = path.join(CONFIG_PATH, 'token')
        self._init_token(token_file)

    def _init_config(self, config_file):
        # check if there is any configuration to load
        if path.isfile(config_file):
            self.parse_config_file(config_file)
        else:
            self.generate_config_file(config_file)
        self.config_file = config_file

    def _init_token(self, token_file):
        if not path.isfile(token_file):
            self.authorize_new_account()
        else:
            self.parse_token_file(token_file)
        self.token_file = token_file

    def load_defaults(self):
        """Load default values into configuration."""
        self.key_bindings = defaults.key_bindings
        self.palette = defaults.palette
        self.styles = defaults.styles
        self.logging_level = defaults.logging_level

    def generate_config_file(self, config_file):
        conf = RawConfigParser()

        # Key bindings
        for category in self.key_bindings:
            conf.add_section(category)
            bindings = self.key_bindings[category]
            for binding_name in bindings:
                key, description = bindings[binding_name]
                conf.set(category, binding_name, key)

        # Color
        conf.add_section('colors')
        for label in self.palette:
            name, fg, bg = label[0], label[1], label[2]
            conf.set('colors', name, fg)
            conf.set('colors', name + '_bg', bg)

        # Styles
        conf.add_section('styles')
        conf.set('styles', 'header_template', self.styles['header_template'])
        conf.set('styles', 'dm_template',     self.styles['dm_template'])

        # Debug
        conf.add_section('debug')
        conf.set('debug', 'logging_level', self.logging_level)

        with open(config_file, 'wb') as config:
            conf.write(config)

        self.config_file = config_file

        print encode(_('Generated configuration file in %s')) % config_file

    def parse_config_file(self, config_file):
        self._conf = RawConfigParser()
        self._conf.read(config_file)

        self._parse_key_bindings()
        self._parse_palette()
        self._parse_styles()
        self._parse_debug()

    def _parse_key_bindings(self):
        for category in self.key_bindings:
            bindings = self.key_bindings[category]
            for binding_name in bindings:
                if self._conf.has_option(category, binding_name):
                    key, description = bindings[binding_name]
                    custom_key = self._conf.get(category, binding_name) 
                    bindings[binding_name] = custom_key, description

    def _parse_palette(self):
        pass

    def _parse_styles(self):
        pass

    def _parse_debug(self):
        pass

    def parse_token_file(self, token_file):
        pass

    def authorize_new_account(self):
        access_token = authorization()
        if access_token:
            self.oauth_token = access_token['oauth_token']
            self.create_token_file(self.token_file,
                                   access_token['oauth_token'],
                                   access_token['oauth_token_secret'])
        else:
            # TODO: exit codes
            exit(2)

    def create_token_file(self, 
                          token_file,
                          oauth_token,
                          oauth_token_secret):
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

        conf = RawConfigParser()
        conf.add_section('token')
        conf.set('token', 'oauth_token', oauth_token)
        conf.set('token', 'oauth_token_secret', oauth_token_secret)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)

        print encode(_('your account has been saved'))
