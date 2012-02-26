###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import os
import sys
import logging
import ConfigParser
import oauth2 as oauth
from curses import ascii
from gettext import gettext as _

try:
    from urlparse import parse_qsl
except ImportError:
    pass
    #from cgi import parse_qsl

import constant
from util import encode

def print_ask_service(token_file):
    print ''
    print encode(_('Couldn\'t find any profile.'))
    print ''
    print encode(_('It should reside in: %s')) % token_file
    print encode(_('If you want to setup a new account, then follow these steps'))
    print encode(_('If you want to skip this, just press return or ctrl-C.'))
    print ''

    print ''
    print encode(_('Which service do you want to use?'))
    print ''
    print '1. Twitter'
    print '2. Identi.ca'
    print ''

def print_ask_root_url():
    print ''
    print ''
    print encode(_('Which root url do you want? (leave blank for default, https://identi.ca/api)'))
    print ''


class Configuration(object):
    """Class responsible for managing the configuration."""

    def __init__(self, args):
        self.init_config()
        self.home = os.environ['HOME']
        self.get_xdg_config()
        self.get_browser()
        # generate the config file
        if args.generate_config != None:
            self.generate_config_file(args.generate_config)
            sys.exit(0)

        self.set_path(args)
        self.check_for_default_config()
        self.conf = ConfigParser.RawConfigParser()
        self.conf.read(self.config_file)
        if not os.path.isfile(self.token_file):
            self.new_account()
        else:
            self.parse_token()

        self.parse_config()

    def init_config(self):
        self.token     = constant.token
        self.keys      = constant.key
        self.params    = constant.params
        self.filter    = constant.filter
        self.palette   = constant.palette

    def get_xdg_config(self):
        try:
            self.xdg_config = os.environ['XDG_CONFIG_HOME']
        except:
            self.xdg_config = self.home+'/.config'

    def get_browser(self):
        try:
            self.browser    = os.environ['BROWSER']
        except:
            self.browser    = ''

    def check_for_default_config(self):
        default_dir = '/turses'
        default_file = '/turses/turses.cfg'
        if not os.path.isfile(self.xdg_config + default_file):
            if not os.path.exists(self.xdg_config + default_dir):
                try:
                    os.makedirs(self.xdg_config + default_dir)
                except:
                    print encode(_('Couldn\'t create the directory in %s/turses')) % self.xdg_config
            self.generate_config_file(self.xdg_config + default_file)


    def generate_config_file(self, config_file):
        conf = ConfigParser.RawConfigParser()
        conf.read(config_file)

        # COLOR
        conf.add_section('colors')
        for c in self.palette:
            conf.set('colors', c[0], c[1])
        # KEYS
        conf.add_section('keys')
        for k in self.keys:
            conf.set('keys', k, self.keys[k])
        # PARAMS
        conf.add_section('params')
        for p in self.params:
            if self.params[p] == True:
                value = 1
            elif self.params[p] == False:
                value = 0
            elif self.params[p] == None:
                continue
            else:
                value = self.params[p]

            conf.set('params', p, value)

        with open(config_file, 'wb') as config:
            conf.write(config)

        print encode(_('Generating configuration file in %s')) % config_file

    def set_path(self, args):
        # Default config path set
        if self.xdg_config != '':
            self.turses_path = self.xdg_config + '/turses/'
        else:
            self.turses_path = self.home + '/.config/turses/'
        # Setup the token file
        self.token_file = self.turses_path + 'turses.tok'
        if args.account != None:
            self.token_file += '.' + args.account
        # Setup the config file
        self.config_file = self.turses_path + 'turses.cfg'
        if args.config != None:
            self.config_file += '.' + args.config

    def new_account(self):

        choice = self.ask_service()
        if choice == '2':
            self.ask_root_url()

        self.authorization()
        self.createTokenFile()

    def ask_service(self):
        print_ask_service(self.token_file)
        choice = raw_input(encode(_('Your choice? > ')))

        if choice == '1':
            self.service = 'twitter'
        elif choice == '2':
            self.service = 'identica'
        else:
            sys.exit(1)
        return choice

    def ask_root_url(self):
        print_ask_root_url()
        url = raw_input(encode(_('Your choice? > ')))
        if url == '':
            self.base_url = 'https://identi.ca/api'
        else:
            self.base_url = url

    def parse_token(self):
        token = ConfigParser.RawConfigParser()
        token.read(self.token_file)
        if token.has_option('token', 'service'):
            self.service = token.get('token', 'service')
        else:
            self.service = 'twitter'

        if token.has_option('token', 'base_url'):
            self.base_url = token.get('token', 'base_url')

        self.oauth_token = token.get('token', 'oauth_token')
        self.oauth_token_secret = token.get('token', 'oauth_token_secret')

    def parse_config(self):
        self.parse_color()
        self.parse_keys()
        self.parse_params()
        self.parse_filter()
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
        if self.conf.has_option('params', 'openurl_command'):
            self.params['openurl_command'] = self.conf.get('params',
                'openurl_command')
        elif self.browser != '':
            self.params['openurl_command'] = self.browser + ' %s'

        if self.conf.has_option('params', 'open_image_command'):
            self.params['open_image_command'] = self.conf.get('params',
                'open_image_command')

        # Transparency
        if self.conf.has_option('params', 'transparency'):
            if int(self.conf.get('params', 'transparency')) == 0:
                self.params['transparency'] = False
        # Compress display
        if self.conf.has_option('params', 'compact'):
            if int(self.conf.get('params', 'compact')) == 1:
                self.params['compact'] = True
        # Help bar
        if self.conf.has_option('params', 'help'):
            if int(self.conf.get('params', 'help')) == 0:
                self.params['help'] = False

        if self.conf.has_option('params', 'margin'):
            self.params['margin'] = int(self.conf.get('params', 'margin'))

        if self.conf.has_option('params', 'padding'):
            self.params['padding'] = int(self.conf.get('params', 'padding'))

        if self.conf.has_option('params', 'old_skool_border'):
            if int(self.conf.get('params', 'old_skool_border')) == 1:
                self.params['old_skool_border'] = True

        if self.conf.has_option('params', 'consumer_key'):
            self.token['identica']['consumer_key'] = self.conf.get('params', 'consumer_key')

        if self.conf.has_option('params', 'consumer_secret'):
            self.token['identica']['consumer_secret'] = self.conf.get('params', 'consumer_secret')

        if self.conf.has_option('params', 'logging_level'):
            self.params['logging_level'] = self.conf.get('params', 'logging_level')

        if self.conf.has_option('params', 'header_template'):
            self.params['header_template'] = self.conf.get('params', 'header_template')

        if self.conf.has_option('params', 'proxy'):
            self.params['proxy'] = self.conf.get('params', 'proxy')

        if self.conf.has_option('params', 'beep'):
            self.params['beep'] = self.conf.getboolean('params', 'beep')

    def parse_filter(self):
        if self.conf.has_option('filter', 'activate'):
            if int(self.conf.get('filter', 'activate')) == 1:
                self.filter['activate'] = True

        if self.conf.has_option('filter', 'myself'):
            if int(self.conf.get('filter', 'myself')) == 1:
                self.filter['myself'] = True

        if self.conf.has_option('filter', 'behavior'):
            self.filter['behavior'] = self.conf.get('filter', 'behavior')

        if self.conf.has_option('filter', 'except'):
            self.filter['except'] = self.conf.get('filter', 'except').split(' ')

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
        lvl = int(self.params['logging_level'])
        if lvl == 1:
            return logging.DEBUG
        elif lvl == 2:
            return logging.INFO
        elif lvl == 3:
            return logging.WARNING
        elif lvl == 4:
            return logging.ERROR

    def authorization(self):
        ''' This function from python-twitter developers '''
        # Copyright 2007 The Python-Twitter Developers
        #
        # Licensed under the Apache License, Version 2.0 (the "License");
        # you may not use this file except in compliance with the License.
        # You may obtain a copy of the License at
        #
        #     http://www.apache.org/licenses/LICENSE-2.0
        #
        # Unless required by applicable law or agreed to in writing, software
        # distributed under the License is distributed on an "AS IS" BASIS,
        # WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
        # See the License for the specific language governing permissions and
        # limitations under the License.

        if self.service == 'twitter':
            base_url = 'https://api.twitter.com'
            self.base_url = base_url
        else:
            base_url = self.base_url

        print 'base_url:{0}'.format(base_url)


        REQUEST_TOKEN_URL          = base_url + '/oauth/request_token'
        if self.service == 'identica':
            if base_url != 'https://identi.ca/api':
                self.parse_config()
            REQUEST_TOKEN_URL += '?oauth_callback=oob'

        ACCESS_TOKEN_URL           = base_url + '/oauth/access_token'
        AUTHORIZATION_URL          = base_url + '/oauth/authorize'
        consumer_key               = self.token[self.service]['consumer_key']
        consumer_secret            = self.token[self.service]['consumer_secret']
        oauth_consumer             = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        oauth_client               = oauth.Client(oauth_consumer)

        print encode(_('Requesting temp token from ')) + self.service.capitalize()

        resp, content = oauth_client.request(REQUEST_TOKEN_URL, 'GET')

        if resp['status'] != '200':
            print encode(_('Invalid respond from ')) +self.service.capitalize() + encode(_(' requesting temp token: %s')) % str(resp['status'])
        else:
            request_token = dict(parse_qsl(content))

            print ''
            print encode(_('Please visit the following page to retrieve pin code needed'))
            print encode(_('to obtain an Authentication Token:'))
            print ''
            print '%s?oauth_token=%s' % (AUTHORIZATION_URL, request_token['oauth_token'])
            print ''

            pincode = raw_input('Pin code? ')

            token = oauth.Token(request_token['oauth_token'], request_token['oauth_token_secret'])
            token.set_verifier(pincode)

            print ''
            print encode(_('Generating and signing request for an access token'))
            print ''

            oauth_client  = oauth.Client(oauth_consumer, token)
            resp, content = oauth_client.request(ACCESS_TOKEN_URL, method='POST', body='oauth_verifier=%s' % pincode)
            access_token  = dict(parse_qsl(content))

            if resp['status'] != '200':
                print 'response:{0}'.format(resp['status'])
                print encode(_('Request for access token failed: %s')) % resp['status']
                print access_token
                sys.exit()
            else:
                self.oauth_token = access_token['oauth_token']
                self.oauth_token_secret = access_token['oauth_token_secret']

    def createTokenFile(self):
        if not os.path.isdir(self.turses_path):
            try:
                os.mkdir(self.turses_path)
            except:
                print encode(_('Error creating directory .config/turses'))

        conf = ConfigParser.RawConfigParser()
        conf.add_section('token')
        conf.set('token', 'service', self.service)
        conf.set('token', 'base_url', self.base_url)
        conf.set('token', 'oauth_token', self.oauth_token)
        conf.set('token', 'oauth_token_secret', self.oauth_token_secret)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)

        print encode(_('your account has been saved'))

    def load_last_read(self):
        try:
            conf = ConfigParser.RawConfigParser()
            conf.read(self.token_file)
            return conf.get('token', 'last_read')
        except:
            return False

    def save_last_read(self, last_read):
        conf = ConfigParser.RawConfigParser()
        conf.read(self.token_file)
        conf.set('token', 'last_read', last_read)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)
