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

import logging
from curses import ascii
from ConfigParser import RawConfigParser
from os import environ, path, mkdir
from gettext import gettext as _

from . import defaults
from .utils import encode
from .api.base import authorization


HOME = environ['HOME']
CONFIG_DIR = '.turses'
CONFIG_PATH = path.join(HOME, CONFIG_DIR)

class TursesConfiguration(object):
    """
    Create and parse configuration files.

    Has backwards compatibility with the Tyrs legacy configuration.
    """
    def __init__(self, cli_args):
        """
        Create a `Configuration` object taking into account the arguments
        provided in the command line interface.
        """
        self.load_defaults()

        self.home = environ['HOME']
        self.browser = environ['BROWSER']

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
        #conf.read(config_file)

        # Key bindings
        for category in self.key_bindings.keys():
            conf.add_section(category)
            for keyword, key, description in self.key_bindings[category]:
                conf.set(category, keyword, key)

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
        pass

    def parse_token_file(self, token_file):
        pass

    def authorize_new_account(self):
        access_token = authorization()
        if access_token:
            self.oauth_token = access_token['oauth_token']
            self.oauth_token_secret = access_token['oauth_token_secret']
        else:
            exit(2)

    def create_token_file(self, token_file):
        conf = RawConfigParser()

        conf.add_section('token')
        conf.set('token', 'oauth_token', self.oauth_token)
        conf.set('token', 'oauth_token_secret', self.oauth_token_secret)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)

        print encode(_('your account has been saved'))


class Configuration(object):
    """Class responsible for managing the configuration."""

    def __init__(self, args):
        # read defaults
        self.init_config()
        # read environment variables
        self.home = environ['HOME']
        self.browser = environ['BROWSER']
        self.get_xdg_config()
        self.get_browser()

        # generate the config file
        if args.generate_config:
            self.generate_config_file(args.generate_config)
            exit(0)

        self.set_path(args)
        self.check_for_default_config()
        self.conf = RawConfigParser()
        self.conf.read(self.config_file)

        if not path.isfile(self.token_file):
            self.new_account()
        else:
            self.parse_token()

        self.parse_config()

    def init_config(self):
        self.keys    = defaults.key
        self.params  = defaults.params
        self.palette = defaults.palette

    def get_browser(self):
        try:
            self.browser = environ['BROWSER']
        except:
            self.browser = ''

    def new_account(self):
        authorization()
        self.createTokenFile()

    def parse_token(self):
        token = RawConfigParser()
        token.read(self.token_file)

        self.oauth_token = token.get('token', 'oauth_token')
        self.oauth_token_secret = token.get('token', 'oauth_token_secret')

    def parse_config(self):
        self.parse_color()
        self.parse_keys()
        self.parse_params()
        self.init_logger()

    def parse_color(self):
        for i, c in enumerate(self.palette):
            if self.conf.has_option('colors', c[0]):
                self.palette[i][1] = (self.conf.get('colors', c[0]))

    def parse_keys(self):
        for key in self.keys:
            if self.conf.has_option('keys', key):
                self.keys[key] = self.conf.get('keys', key)
            else:
                self.keys[key] = self.keys[key]

    def char_value(self, ch):
        if ch[0] == '^':
            i = 0
            while i <= 31:
                if ascii.unctrl(i) == ch.upper():
                    return i
                i +=1
        return ord(ch)

    def parse_params(self):

        # refresh (in minutes)
        if self.conf.has_option('params', 'refresh'):
            self.params['refresh']     = int(self.conf.get('params', 'refresh'))

        if self.conf.has_option('params', 'box_position'):
            self.params['refresh']     = int(self.conf.get('params', 'box_position'))

        # tweet_border
        if self.conf.has_option('params', 'tweet_border'):
            self.params['tweet_border'] = int(self.conf.get('params', 'tweet_border'))

        # Relative_time
        if self.conf.has_option('params', 'relative_time'):
            self.params['relative_time'] = int(self.conf.get('params', 'relative_time'))

        # Retweet_By
        if self.conf.has_option('params', 'retweet_by'):
            self.params['retweet_by'] = int(self.conf.get('params', 'retweet_by'))

        # Openurl_command
        #  NOTE: originally `openurl_command` configuration parameter was
        #        prioritary but I'm deprecating this, using the BROWSER
        #        environment variable instead.
        if self.browser != '':
            self.params['openurl_command'] = self.browser
        elif self.conf.has_option('params', 'openurl_command'):
            self.params['openurl_command'] = self.conf.get('params',
                'openurl_command')

        if self.conf.has_option('params', 'logging_level'):
            self.params['logging_level'] = self.conf.get('params', 'logging_level')

        if self.conf.has_option('params', 'header_template'):
            self.params['header_template'] = self.conf.get('params', 'header_template')

        if self.conf.has_option('params', 'dm_template'):
            self.params['dm_template'] = self.conf.get('params', 'dm_template')

    def init_logger(self):
        log_file = self.xdg_config + '/turses/turses.log'
        lvl = self.init_logger_level()

        logging.basicConfig(
            filename=log_file,
            level=lvl,
            format='%(asctime)s %(levelname)s - %(message)s',
            datefmt='%d/%m/%Y %H:%M:%S',
            )
        logging.info('turses starting...')

    def init_logger_level(self):
        try:
            lvl = int(self.params['logging_level'])
        except:
            # INFO is the default logging level
            return logging.INFO

        if lvl == 1:
            return logging.DEBUG
        elif lvl == 2:
            return logging.INFO
        elif lvl == 3:
            return logging.WARNING
        elif lvl == 4:
            return logging.ERROR

    def createTokenFile(self):
        if not path.isdir(self.turses_path):
            try:
                mkdir(self.turses_path)
            except:
                print encode(_('Error creating directory .config/turses'))

        conf = RawConfigParser()

        conf.add_section('token')
        conf.set('token', 'oauth_token', self.oauth_token)
        conf.set('token', 'oauth_token_secret', self.oauth_token_secret)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)

        print encode(_('your account has been saved'))

    def save_last_read(self, last_read):
        conf = RawConfigParser()
        conf.read(self.token_file)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)
