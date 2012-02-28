###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from gettext import gettext as _

import urwid

def help_bar(configuration):
    if configuration.params['help']:
        return urwid.AttrWrap(urwid.Columns([
            urwid.Text(['help:', ('help_key', ' ? ')]),
            urwid.Text(['up:', ('help_key', ' %s ' % configuration.keys['up'])]),
            urwid.Text(['down:', ('help_key', ' %s ' % configuration.keys['down'])]),
            urwid.Text(['tweet:', ('help_key', ' %s ' % configuration.keys['tweet'])]),
            ('fixed', 12, urwid.Text(['retweet:', ('help_key', ' %s ' %
                                                   configuration.keys['retweet'])])),
            urwid.Text(['reply:', ('help_key', ' %s ' % configuration.keys['reply'])]),
            urwid.Text(['quit:', ('help_key', ' %s ' % configuration.keys['quit'])]),
        ]), 'help_bar')
    else:
        return None

class HelpBuffer(urwid.WidgetWrap):
    """
    A widget that displays all the keybindings of the given configuration.
    """

    col = [30, 7]

    def __init__ (self, configuration):
        self.configuration = configuration
        self.items = []
        w = urwid.AttrWrap(self.create_help_buffer(), 'body')
        self.__super.__init__(w)

    def create_help_buffer(self):
        self.insert_header()
        # Motion
        self.insert_division(_('Motion'))
        self.insert_help_item('up', _('Scroll up one tweet'))
        self.insert_help_item('down', _('Scroll down one tweet'))
        self.insert_help_item('left', _('Activate the timeline on the left'))
        self.insert_help_item('right', _('Activate the timeline on the right'))
        self.insert_help_item('scroll_to_top', _('Scroll to first tweet'))
        self.insert_help_item('scroll_to_bottom', _('Scroll to last tweet'))

        self.insert_division(_('Buffers'))
        self.insert_help_item('shift_buffer_left', _('Shift active buffer one position to the left'))
        self.insert_help_item('shift_buffer_right', _('Shift active buffer one position to the right'))
        self.insert_help_item('shift_buffer_beggining', _('Shift active buffer to the beggining'))
        self.insert_help_item('shift_buffer_end', _('Shift active buffer to the end'))
        self.insert_help_item('activate_first_buffer', _('Activate first buffer'))
        self.insert_help_item('activate_last_buffer', _('Activate last buffer'))
        self.insert_help_item('delete_buffer', _('Delete active buffer'))
        self.insert_help_item('clear', _('Clear active buffer'))

        # Twitter
        self.insert_division(_('Tweets'))
        self.insert_help_item('tweet', _('Compose a tweet'))
        self.insert_help_item('delete_tweet', _('Delete selected tweet (must be yours)'))
        self.insert_help_item('reply', _('Reply to selected tweet'))
        self.insert_help_item('retweet', _('Retweet selected tweet'))
        self.insert_help_item('retweet_and_edit', _('Retweet selected tweet editing it first'))
        self.insert_help_item('sendDM', _('Send direct message'))
        self.insert_help_item('update', _('Refresh current timeline'))

        self.insert_division(_('Friendship'))
        self.insert_help_item('follow_selected', _('Follow selected twitter'))
        self.insert_help_item('unfollow_selected', _('Unfollow selected twitter'))
        self.insert_help_item('follow', _('Follow a twitter'))
        self.insert_help_item('unfollow', _('Unfollow a twitter'))

        self.insert_division(_('Favorites'))
        self.insert_help_item('fav', _('Mark selected tweet as favorite'))
        self.insert_help_item('get_fav', _('Go to favorites timeline'))
        self.insert_help_item('delete_fav', _('Remove a tweet from favorites'))

        self.insert_division(_('Timelines'))
        self.insert_help_item('home', _('Go to home timeline'))
        self.insert_help_item('mentions', _('Go to mentions timeline'))
        self.insert_help_item('DMs', _('Go to direct message timeline'))
        self.insert_help_item('search', _('Search for term and show resulting timeline'))
        self.insert_help_item('search_user', _('Show somebody\'s public timeline'))
        self.insert_help_item('search_myself', _('Show your public timeline'))
        self.insert_help_item('thread', _('Open selected thread'))
        self.insert_help_item('user_info', _('Show user information '))
        self.insert_help_item('help', _('Show help buffer'))

        # Others
        self.insert_division(_('Others'))
        self.insert_help_item('quit', _('Leave turses'))
        self.insert_help_item('openurl', _('Open URL in browser'))
        self.insert_help_item('open_image', _('Open image'))
        self.insert_help_item('redraw', _('Redraw the screen'))

        return urwid.ListBox(urwid.SimpleListWalker(self.items))

    def insert_division(self, title):
        self.items.append(urwid.Divider(' '))
        self.items.append(urwid.Padding(urwid.AttrWrap(urwid.Text(title), 'focus'), left=4))
        self.items.append(urwid.Divider(' '))

    def insert_header(self):
        self.items.append( urwid.Columns([
            ('fixed', self.col[0], urwid.Text('  Name')),
            ('fixed', self.col[1], urwid.Text('Key')),
            urwid.Text('Description')
        ]))

    def insert_help_item(self, key, description):
        self.items.append( urwid.Columns([
            ('fixed', self.col[0], urwid.Text('  ' + key)),
            ('fixed', self.col[1], urwid.Text(self.configuration.keys[key])),
            urwid.Text(description)
        ]))
