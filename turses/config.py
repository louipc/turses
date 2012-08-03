# -*- coding: utf-8 -*-

"""
The configuration files are located on ``$HOME/.turses`` directory.

There is one mayor configuration file in turses:

    ``config``
        contains user preferences: colors, bindings, etc.

An one default token file:

    ``token``
        contains authentication token for the default user account

Each user account that is no the default one needs to be aliased and  has its
own token file ``alias.token``.

To create an aliased account:

.. code-block:: sh

    $ turses -a work

And, after authorizing ``turses`` to use that account,  a token file named
``work.token`` will be created. Optionally you can create a ``work.config``
file for a configuration specific to that account.

Now, when you execute again:

.. code-block:: sh

    $ turses -a work

you will be logged in with the previously stored credentials.

Here is an example with two accounts apart from the default one, aliased
to ``alice`` and ``bob``.

.. code-block:: sh

    ~
    |+.turses/
    | |-config
    | |-alice.config
    | |-token
    | |-alice.token
    | `-bob.token
    |+...
    |-...
    `


If you want to generate a configuration file, you can do so executing:

.. code-block:: sh

    $ turses -g /path/to/file
"""

from sys import exit
from ConfigParser import RawConfigParser
from os import getenv, path, mkdir, remove
from functools import partial
from gettext import gettext as _

from turses.utils import encode
from turses.meta import wrap_exceptions
from turses.api.base import get_authorization_tokens

# -- Defaults -----------------------------------------------------------------

# Timelines

HOME_TIMELINE = 'home'
MENTIONS_TIMELINE = 'mentions'
FAVORITES_TIMELINE = 'favorites'
MESSAGES_TIMELINE = 'messages'
OWN_TWEETS_TIMELINE = 'own_tweets'

DEFAULT_TIMELINES = {
    HOME_TIMELINE:       True,
    MENTIONS_TIMELINE:   True,
    FAVORITES_TIMELINE:  True,
    MESSAGES_TIMELINE:   True,
    OWN_TWEETS_TIMELINE: True,
}

# Key bindings

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
    'update_all':
        ('S', _('refresh all the timelines')),
    'tweet_hashtag':
        ('H', _('compose a tweet with the same hashtags as the focused status')),
    'fav':
        ('b', _('mark focused tweet as favorite')),
    'delete_fav':
        ('ctrl b', _('remove tweet from favorites')),
    'follow_selected':
        ('f', _('follow selected status\' author')),
    'follow_user':
        ('F', _('follow user given in an editor')),
    'unfollow_selected':
        ('U', _('unfollow selected status\' author')),
    'unfollow_user':
        ('ctrl u', _('unfollow user given in an editor')),

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
    'retweets_of_me':
        ('I', _('open a timeline with your tweets that have been retweeted')),

    # info
    'user_info':
        ('i', _('show user\'s info')),

    # meta
    'help':
        ('?', _('show program help')),
    'reload_config':
        ('C', _('reload configuration')),

    # turses
    'quit':
        ('q', _('exit program')),
    'clear':
        ('c', _('clear status bar')),
    'openurl':
        ('o', _('open URLs of the focused status in a browser')),
    'open_status_url':
        ('O', _('open the focused status in a browser')),
    'redraw':
        ('ctrl l', _('redraw the screen')),
}

# NOTE:
# The key binding categories are declared to order them in the configuration
# and in the help buffer. If you add a key binding, don't forget to include
# it in one of these categories.

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
    'update_all',
    'tweet_hashtag',
    'fav',
    'delete_fav',
    'follow_selected',
    'follow_user',
    'unfollow_selected',
    'unfollow_user',
    'user_info',
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
    'retweets_of_me',
]

META_KEY_BINDINGS = [
    'help',
    'reload_config',
]

TURSES_KEY_BINDINGS = [
    'clear',
    'quit',
    'openurl',
    'open_status_url',
    'redraw',
]

# Palette

# TODO: not hard coded
# valid colors for `urwid`s palette
VALID_COLORS = [
    'default',
    'black',
    'dark red',
    'dark green',
    'brown',
    'dark blue',
    'dark magenta',
    'dark cyan',
    'light gray',
    'dark gray',
    'light red',
    'light green',
    'yellow',
    'light blue',
    'light magenta',
    'light cyan',
    'white',
]


def validate_color(colorstring):
    return colorstring if colorstring in VALID_COLORS else ''

PALETTE = [
    #Tabs
    ['active_tab',  'white', 'dark blue'],
    ['visible_tab', 'yellow', 'dark blue'],
    ['inactive_tab', 'dark blue', ''],

    # Statuses
    ['header', 'light blue', ''],
    ['body', 'white', ''],
    ['focus', 'light red', ''],
    ['line', 'black', ''],
    ['unread', 'dark red', ''],
    ['read', 'dark blue', ''],
    ['favorited', 'yellow', ''],

    # Text
    ['highlight', 'dark red', ''],
    ['highlight_nick', 'light red', ''],
    ['attag', 'yellow', ''],
    ['hashtag', 'light red', ''],
    ['url', 'white', 'dark red'],

    # Messages
    ['error', 'white', 'dark red'],
    ['info', 'white', 'dark blue'],

    # Editor
    ['editor', 'white', 'dark blue'],
]

# Styles

STYLES = {
    # TODO: make time string configurable
    'header_template': ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} ',
    'dm_template': ' {sender_screen_name} => {recipient_screen_name} - {time} ',
    'tab_template': '{timeline_name} [{unread}]',
    'box_around_status': True,
    'status_divider': False,
    'status_bar': True,
    'status_divider_char': '─',
    'editor_horizontal_align': 'center',
    'editor_vertical_align': 'bottom',
    'url_format': 'display',
}

# Debug

LOGGING_LEVEL = 3

# Twitter

UPDATE_FREQUENCY = 300

# Environment

HOME = getenv('HOME')

# -- Configuration ------------------------------------------------------------

# Default config path
CONFIG_DIR = '.turses'
CONFIG_PATH = path.join(HOME, CONFIG_DIR)
DEFAULT_CONFIG_FILE = path.join(CONFIG_PATH, 'config')
DEFAULT_TOKEN_FILE = path.join(CONFIG_PATH, 'token')
LOG_FILE = path.join(CONFIG_PATH, 'log')

LEGACY_CONFIG_DIR = '.config/turses'
LEGACY_CONFIG_PATH = path.join(HOME, LEGACY_CONFIG_DIR)
LEGACY_CONFIG_FILE = path.join(LEGACY_CONFIG_PATH, 'turses.cfg')
LEGACY_TOKEN_FILE = path.join(LEGACY_CONFIG_PATH, 'turses.tok')

# Names of the sections in the configuration
SECTION_DEFAULT_TIMELINES = 'timelines'
SECTION_KEY_BINDINGS = 'bindings'
SECTION_PALETTE = 'colors'
SECTION_STYLES = 'styles'
SECTION_DEBUG = 'debug'
SECTION_TWITTER = 'twitter'

# Names of the sections in the token file
SECTION_TOKEN = 'token'


def print_deprecation_notice():
    print "NOTE:"
    print
    print "The configuration file in %s has been deprecated." % LEGACY_CONFIG_FILE
    print "A new configuration directory is being generated in %s." % CONFIG_PATH
    print


class Configuration(object):
    """
    Generate and parse configuration files. When instantiated, it loads the
    defaults.

    Calling :func:`Configuration.parse_args` with an
    :class:`argparse.ArgumentParser` instance will modify the instance to match
    the options provided by the command line arguments.

    Calling :func:`turses.config.Configuration.load` on this class' instances
    reads the preferences from the user configuration files. If no
    configuration or token files are found, this class will take care of
    creating them.

    Offers backwards compatibility with the Tyrs configuration.
    """

    def __init__(self):
        """
        Create a `Configuration` taking into account the arguments
        from the command line interface (if any).
        """
        # load defaults
        self.default_timelines = DEFAULT_TIMELINES
        self.update_frequency = UPDATE_FREQUENCY
        self.key_bindings = KEY_BINDINGS
        self.palette = PALETTE
        self.styles = STYLES
        self.logging_level = LOGGING_LEVEL

        # config and token files
        self.config_file = DEFAULT_CONFIG_FILE
        self.token_file = DEFAULT_TOKEN_FILE

        # debug mode
        self.debug = False

        # create the config directory if it does not exist
        if not path.isdir(CONFIG_PATH):
            try:
                mkdir(CONFIG_PATH)
            except:
                print encode(_('Error creating config directory in %s' % CONFIG_DIR))
                self.exit_with_code(3)

    def parse_args(self, cli_args):
        """Interprets the arguments provided by `cli_args`."""
        # generate config file and exit
        if cli_args and cli_args.generate_config:
            self.generate_config_file(config_file=cli_args.generate_config,)
            self.exit_with_code(0)

        # path to configuration file
        if cli_args and cli_args.config:
            self.config_file = cli_args.config
        elif cli_args and cli_args.account:
            self.config_file = path.join(CONFIG_PATH, '%s.config' % cli_args.account)

        # path to token file
        if cli_args and cli_args.account:
            self.token_file = path.join(CONFIG_PATH, '%s.token' % cli_args.account)

        # debug mode
        self.debug = getattr(cli_args, 'debug', False)

    def load(self):
        """
        Loads configuration from files.
        """
        self._init_config()
        self._init_token()

    def _init_config(self):
        if path.isfile(LEGACY_CONFIG_FILE):
            self._parse_legacy_config_file()
            print_deprecation_notice()
            remove(LEGACY_CONFIG_FILE)
        elif path.isfile(self.config_file):
            self.parse_config_file(self.config_file)
        else:
            self.generate_config_file(self.config_file)

    def _add_section_default_timelines(self, conf):
        # Default timelines
        if not conf.has_section(SECTION_DEFAULT_TIMELINES):
            conf.add_section(SECTION_DEFAULT_TIMELINES)
        for timeline in DEFAULT_TIMELINES:
            if conf.has_option(SECTION_DEFAULT_TIMELINES, timeline):
                continue
            value = str(self.default_timelines[timeline]).lower()
            conf.set(SECTION_DEFAULT_TIMELINES, timeline, value)

    def _add_section_twitter(self, conf):
        # Twitter
        if not conf.has_section(SECTION_TWITTER):
            conf.add_section(SECTION_TWITTER)
        if conf.has_option(SECTION_TWITTER, 'update_frequency'):
            return
        else:
            conf.set(SECTION_TWITTER, 'update_frequency', UPDATE_FREQUENCY)

    def _add_section_key_bindings(self, conf):
        # Key bindings
        if not conf.has_section(SECTION_KEY_BINDINGS):
            conf.add_section(SECTION_KEY_BINDINGS)
        binding_lists = [MOTION_KEY_BINDINGS,
                         BUFFERS_KEY_BINDINGS,
                         TWEETS_KEY_BINDINGS,
                         TIMELINES_KEY_BINDINGS,
                         META_KEY_BINDINGS,
                         TURSES_KEY_BINDINGS, ]
        for binding_list in binding_lists:
            for binding in binding_list:
                key = self.key_bindings[binding][0]
                if conf.has_option(SECTION_KEY_BINDINGS, binding):
                    continue
                conf.set(SECTION_KEY_BINDINGS, binding, key)

    def _add_section_palette(self, conf):
        # Color
        if not conf.has_section(SECTION_PALETTE):
            conf.add_section(SECTION_PALETTE)
        for label in PALETTE:
            label_name, fg, bg = label[0], label[1], label[2]

            # fg
            if conf.has_option(SECTION_PALETTE, label_name) and \
                validate_color(conf.get(SECTION_PALETTE, label_name)):
                pass
            else:
                conf.set(SECTION_PALETTE, label_name, fg)

            #bg
            label_name_bg = label_name + '_bg'
            if conf.has_option(SECTION_PALETTE, label_name_bg) and \
                validate_color(conf.get(SECTION_PALETTE, label_name_bg)):
                pass
            else:
                conf.set(SECTION_PALETTE, label_name_bg, bg)

    def _add_section_styles(self, conf):
        # Styles
        if not conf.has_section(SECTION_STYLES):
            conf.add_section(SECTION_STYLES)
        for style in STYLES:
            if conf.has_option(SECTION_STYLES, style):
                continue
            conf.set(SECTION_STYLES, style, self.styles[style])

    def _add_section_debug(self, conf):
        # Debug
        if not conf.has_section(SECTION_DEBUG):
            conf.add_section(SECTION_DEBUG)
        if conf.has_option(SECTION_DEBUG, 'logging_level'):
            return
        conf.set(SECTION_DEBUG, 'logging_level', LOGGING_LEVEL)

    def _init_token(self):
        if path.isfile(LEGACY_TOKEN_FILE):
            self.parse_token_file(LEGACY_TOKEN_FILE)
            remove(LEGACY_TOKEN_FILE)
            if (hasattr(self, 'oauth_token') and
                hasattr(self, 'oauth_token_secret')):
                self.generate_token_file(self.token_file,
                                         self.oauth_token,
                                         self.oauth_token_secret)
        elif not path.isfile(self.token_file):
            self.authorize_new_account()
        else:
            self.parse_token_file(self.token_file)

    def _parse_legacy_config_file(self):
        """
        Parse a legacy configuration file.
        """
        conf = RawConfigParser()
        conf.read(LEGACY_CONFIG_FILE)

        styles = self.styles.copy()

        if conf.has_option('params', 'dm_template'):
            styles['dm_template'] = conf.get('params', 'dm_template')

        if conf.has_option('params', 'header_template'):
            styles['header_template'] = conf.get('params', 'header_template')

        self.styles.update(styles)

        if conf.has_option('params', 'logging_level'):
            self.logging_level = conf.getint('params', 'logging_level')

        for binding in self.key_bindings:
            if conf.has_option('keys', binding):
                custom_key = conf.get('keys', binding)
                self._set_key_binding(binding, custom_key)

        palette_labels = [color[0] for color in PALETTE]
        for label in palette_labels:
            if conf.has_option('colors', label):
                custom_fg = conf.get('colors', label)
                self._set_color(label, custom_fg)

    def _parse_legacy_token_file(self):
        conf = RawConfigParser()
        conf.read(LEGACY_TOKEN_FILE)

        if conf.has_option(SECTION_TOKEN, 'oauth_token'):
            self.oauth_token = conf.get(SECTION_TOKEN, 'oauth_token')

        if conf.has_option(SECTION_TOKEN, 'oauth_token'):
            self.oauth_token_secret = conf.get(SECTION_TOKEN, 'oauth_token_secret')

    def _set_color(self, color_label, custom_fg=None, custom_bg=None):
        for color in self.palette:
            label, fg, bg = color[0], color[1], color[2]
            if label == color_label:
                color[1] = custom_fg if validate_color(custom_fg) is not None else fg
                color[2] = custom_bg if validate_color(custom_bg) is not None else bg

    def _set_key_binding(self, binding, new_key):
        if not binding in self.key_bindings:
            return

        key, description = self.key_bindings[binding]
        new_key_binding = new_key, description
        self.key_bindings[binding] = new_key_binding

    def generate_config_file(self, config_file):
        kwargs = {
            'config_file': config_file,
            'on_error': partial(self._config_generation_error, config_file),
        }

        if not path.isfile(config_file):
            kwargs.update({
                'on_success': partial(self._config_generation_success,
                                      config_file)
            })

        self._generate_config_file(**kwargs)

    @wrap_exceptions
    def _generate_config_file(self, config_file):
        conf = RawConfigParser()

        self._add_section_default_timelines(conf)
        self._add_section_twitter(conf)
        self._add_section_key_bindings(conf)
        self._add_section_palette(conf)
        self._add_section_styles(conf)
        self._add_section_debug(conf)

        with open(config_file, 'wb') as config:
            conf.write(config)

    def _config_generation_success(self, config_file):
        print encode(_('Generated configuration file in %s')) % config_file

    def _config_generation_error(self, config_file):
        print encode(_('Unable to generate configuration file in %s')) % config_file
        self.exit_with_code(2)

    def generate_token_file(self,
                            token_file,
                            oauth_token,
                            oauth_token_secret):
        self.oauth_token = oauth_token
        self.oauth_token_secret = oauth_token_secret

        conf = RawConfigParser()
        conf.add_section(SECTION_TOKEN)
        conf.set(SECTION_TOKEN, 'oauth_token', oauth_token)
        conf.set(SECTION_TOKEN, 'oauth_token_secret', oauth_token_secret)

        with open(token_file, 'wb') as tokens:
            conf.write(tokens)

        print encode(_('your account has been saved'))

    def parse_config_file(self, config_file):
        conf = RawConfigParser()
        conf.read(config_file)

        self._parse_default_timelines(conf)
        self._parse_twitter(conf)
        self._parse_key_bindings(conf)
        self._parse_palette(conf)
        self._parse_styles(conf)
        self._parse_debug(conf)

    def _parse_default_timelines(self, conf):
        for timeline in self.default_timelines:
            if conf.has_option(SECTION_DEFAULT_TIMELINES, timeline):
                try:
                    value = conf.getboolean(SECTION_DEFAULT_TIMELINES,
                                            timeline)
                except ValueError:
                    continue
                self.default_timelines[timeline] = value

    def _parse_twitter(self, conf):
        if conf.has_option(SECTION_TWITTER, 'update_frequency'):
            self.update_frequency = conf.getint(SECTION_TWITTER, 'update_frequency')

    def _parse_key_bindings(self, conf):
        for binding in self.key_bindings:
            if conf.has_option(SECTION_KEY_BINDINGS, binding):
                custom_key = conf.get(SECTION_KEY_BINDINGS, binding)
                self._set_key_binding(binding, custom_key)

    def _parse_palette(self, conf):
        # Color
        for label in self.palette:
            label_name, fg, bg = label[0], label[1], label[2]
            if conf.has_option(SECTION_PALETTE, label_name):
                fg = conf.get(SECTION_PALETTE, label_name)
            if conf.has_option(SECTION_PALETTE, label_name + '_bg'):
                bg = conf.get(SECTION_PALETTE, label_name + '_bg')
            self._set_color(label_name, fg, bg)

    def _parse_styles(self, conf):
        for style in self.styles:
            if conf.has_option(SECTION_STYLES, style):
                if any([style == 'box_around_status',
                        style == 'status_divider',
                        style == 'status_bar']):
                    self.styles[style] = conf.getboolean(SECTION_STYLES, style)
                elif (style == 'editor_horizontal_align' and
                      style in ['left', 'center', 'right']):
                    self.styles[style] = conf.get(SECTION_STYLES, style)
                elif (style == 'url_format' and
                      style in ['shortened', 'original', 'display']):
                    self.styles[style] = conf.get(SECTION_STYLES, style)
                else:
                    self.styles[style] = unicode(conf.get(SECTION_STYLES, style),
                                                 'utf-8')

    def _parse_debug(self, conf):
        if conf.has_option(SECTION_DEBUG, 'logging_level'):
            self.logging_level = conf.getint(SECTION_DEBUG, 'logging_level')

    def parse_token_file(self, token_file):
        conf = RawConfigParser()
        conf.read(token_file)

        if conf.has_option(SECTION_TOKEN, 'oauth_token'):
            self.oauth_token = conf.get(SECTION_TOKEN, 'oauth_token')
        if conf.has_option(SECTION_TOKEN, 'oauth_token_secret'):
            self.oauth_token_secret = conf.get(SECTION_TOKEN, 'oauth_token_secret')

    def authorize_new_account(self):
        access_tokens = get_authorization_tokens()
        if access_tokens:
            access_token = access_tokens['oauth_token']
            access_token_secret = access_tokens['oauth_token_secret']

            self.oauth_token = access_token
            self.generate_token_file(self.token_file,
                                     access_token,
                                     access_token_secret)
        else:
            # TODO: exit codes
            self.exit_with_code(2)

    def reload(self):
        self.parse_config_file(self.config_file)

    def exit_with_code(self, code):
        """Invoke `sys.exit` with the given status `code`."""
        # This is here because makes testing exit codes easier
        exit(code)


# configuration singleton
configuration = Configuration()
