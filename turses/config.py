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
from os import getenv, path, mkdir
from gettext import gettext as _

from .utils import encode
from .api.base import authorization

# -- Defaults -----------------------------------------------------------------

KEY_BINDINGS = {
    # motion
    'up':
         ('k', _('scroll up')),
    'down':                   
         ('j', _('scroll down')),
    'left':                   
        ('h', _('activate the timeline on the left')),
    'right':                  
        ('l', _('activate the timeline on the right')),
    'scroll_to_top':          
        ('g', _('scroll to top')),
    'scroll_to_bottom':       
        ('G', _('scroll to bottom')),

    # buffers
    'activate_first_buffer':  
       ('a', _('activate first buffer')),
    'activate_last_buffer':   
        ('e', _('activate last buffer')),
    'shift_buffer_beggining': 
        ('ctrl a', _('shift active buffer to the beginning')),
    'shift_buffer_end':       
        ('ctrl e', _('shift active buffer to the end')),
    'shift_buffer_left':      
        ('<', _('shift active buffer one position to the left')),
    'shift_buffer_right':     
        ('>', _('shift active buffer one position to the right')),
    'expand_visible_left':    
        ('p', _('expand visible timelines one column to the left')),
    'expand_visible_right':   
        ('n', _('expand visible timelines one column to the right')),
    'shrink_visible_left':    
        ('P', _('shrink visible timelines one column from the left')),
    'shrink_visible_right':   
        ('N', _('shrink visible timelines one column from the left')),
    'delete_buffer':          
        ('d', _('delete buffer')),
    'clear':                  
        ('c', _('clear status bar')),
    'mark_all_as_read':       
        ('A', _('mark all tweets in the current timeline as read')),

    # tweets
    'tweet':                  
        ('t', _('compose a tweet')),
    'delete_tweet':           
        ('X', _('delete focused status')),
    'reply':                  
        ('r', _('reply to focused status')),
    'retweet':                
        ('R', _('retweet focused status')),
    'retweet_and_edit':       
        ('E', _('open a editor for manually retweeting the focused status')),
    'send_dm':                 
        ('D', _('compose a direct message')),
    'update':                 
        ('u', _('refresh the active timeline')),
    'tweet_hashtag':          
        ('H', _('compose a tweet with the same hashtags as the focused status')),
    'fav':                    
        ('b', _('mark focused tweet as favorite')),
    'delete_fav':             
        ('ctrl b', _('remove tweet from favorites')),
    'follow_selected':        
        ('f', _('follow selected status\' author')),
    'unfollow_selected':      
        ('U', _('unfollow selected status\' author')),

    # timelines
    'home':                   
        ('.', _('open a home timeline')),
    'own_tweets':             
        ('_', _('open a timeline with your tweets')),
    'favorites':              
        ('B', _('open a timeline with your favorites')),
    'mentions':               
        ('m', _('open a mentions timeline')),
    'DMs':                    
        ('M', _('open a direct message timeline')),
    'search':                 
        ('/', _('search for term and show resulting timeline')),
    'search_user':            
        ('@', _('open a timeline with the tweets of the specified user')),
    'user_timeline':          
        ('+', _('open a timeline with the tweets of the focused status\' author')),
    'thread':                 
        ('T', _('open the thread of the focused status')),
    'hashtags':               
        ('L', _('open a search timeline with the hashtags of the focused status')),

    # meta
    'help':                   
        ('?', _('show program help')),

    # turses
    'quit':                   
        ('q', _('exit program')),
    'openurl':              
        ('o', _('open URLs of the focused status in a browser')),
    'redraw':                 
        ('ctrl l', _('redraw the screen')),
}

MOTION_KEY_BINDINGS = [
    'up',
    'down',                   
    'left',                   
    'right',                  
    'scroll_to_top',          
    'scroll_to_bottom',       
]

BUFFERS_KEY_BINDINGS = [
    'activate_first_buffer',  
    'activate_last_buffer',   
    'shift_buffer_beggining', 
    'shift_buffer_end',       
    'shift_buffer_left',      
    'shift_buffer_right',     
    'expand_visible_left',    
    'expand_visible_right',   
    'shrink_visible_left',    
    'shrink_visible_right',   
    'delete_buffer',          
    'clear',                  
    'mark_all_as_read',       
]

TWEETS_KEY_BINDINGS = [
    'tweet',                  
    'delete_tweet',           
    'reply',                  
    'retweet',                
    'retweet_and_edit',       
    'send_dm',                 
    'update',                 
    'tweet_hashtag',          
    'fav',                    
    'delete_fav',             
    'follow_selected',        
    'unfollow_selected',      
]

TIMELINES_KEY_BINDINGS = [
    'home',                   
    'own_tweets',             
    'favorites',              
    'mentions',               
    'DMs',                    
    'search',                 
    'search_user',            
    'user_timeline',          
    'thread',                 
    'hashtags',               
]

META_KEY_BINDINGS = [
    'help',                   
]

TURSES_KEY_BINDINGS = [
    'quit',                   
    'openurl',              
    'redraw',                 
]

PALETTE = [
    #Tabs
    ['active_tab',  'white', ''],
    ['visible_tab', 'light cyan', ''],
    ['inactive_tab', 'dark blue', ''],

    # Statuses
    ['header', 'light blue', ''],
    ['body', 'default', '', 'standout'],
    ['focus','dark red', '', 'standout'],
    ['line', 'dark blue', ''],
    ['unread', 'dark red', ''],
    ['read', 'dark blue', ''],
    ['favorited', 'yellow', ''],

    # Text
    ['highlight', 'dark red', ''],
    ['highlight_nick', 'light red', ''],
    ['attag', 'brown', ''],
    ['hashtag', 'dark green', ''],

    # Messages
    ['error', 'white', 'dark red'],
    ['info', 'white', 'dark blue'],
]

STYLES = {
    # TODO: make time string configurable 
    'header_template':      ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'dm_template':          ' {sender_screen_name} => {recipient_screen_name} - {time} ',
}

# Debug
LOGGING_LEVEL = 3

# Environment
HOME = getenv('HOME')
BROWSER = getenv('BROWSER')

# -- Configuration ------------------------------------------------------------

# Default config path
CONFIG_DIR = '.turses'
CONFIG_PATH = path.join(HOME, CONFIG_DIR)

# Names of the sections in the configuration
SECTION_KEY_BINDINGS = 'bindings'
SECTION_PALETTE = 'colors'
SECTION_STYLES = 'styles'
SECTION_DEBUG = 'debug'


class Configuration(object):
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
        self.key_bindings = KEY_BINDINGS
        self.palette = PALETTE
        self.styles = STYLES
        self.logging_level = LOGGING_LEVEL

    def generate_config_file(self, config_file):
        conf = RawConfigParser()

        # Key bindings
        conf.add_section(SECTION_KEY_BINDINGS)
        binding_lists = [MOTION_KEY_BINDINGS,
                         BUFFERS_KEY_BINDINGS,
                         TWEETS_KEY_BINDINGS,
                         TIMELINES_KEY_BINDINGS,
                         META_KEY_BINDINGS,
                         TURSES_KEY_BINDINGS,]
        for binding_list in binding_lists:
            for binding in binding_list:
                key = self.key_bindings[binding][0]
                conf.set(SECTION_KEY_BINDINGS, binding, key)
        

        # Color
        conf.add_section(SECTION_PALETTE)
        for label in self.palette:
            label_name, fg, bg = label[0], label[1], label[2]
            conf.set(SECTION_PALETTE, label_name, fg)
            conf.set(SECTION_PALETTE, label_name + '_bg', bg)

        # Styles
        conf.add_section(SECTION_STYLES)
        for style in self.styles:
            conf.set(SECTION_STYLES, style, self.styles[style])

        # Debug
        conf.add_section(SECTION_DEBUG)
        conf.set(SECTION_DEBUG, 'logging_level', LOGGING_LEVEL)

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
        for binding in self.key_bindings:
            if self._conf.has_option(SECTION_KEY_BINDINGS, binding):
                key, description = self.key_bindings[binding]
                custom_key = self._conf.get(SECTION_KEY_BINDINGS, binding) 
                self.key_bindings[binding] = custom_key

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

    def save_last_read(self, last_read):
        conf = RawConfigParser()
        conf.read(self.token_file)

        with open(self.token_file, 'wb') as tokens:
            conf.write(tokens)
