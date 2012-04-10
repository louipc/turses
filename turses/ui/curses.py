# -*- coding: utf-8 -*-

"""
turses.ui.curses
~~~~~~~~~~~~~~~~

This module contains the curses implementation of the UI widgets contained
in `turses.ui.base`.
"""

from gettext import gettext as _

from urwid import (
        AttrWrap, 
        WidgetWrap, 
        Padding, 
        WidgetDecoration,
        Divider, 
        SolidFill,

        # widgets
        Text, 
        Edit, 
        Frame, 
        Columns, 
        Pile, 
        ListBox, 
        SimpleListWalker,

        # signals
        signals, 
        emit_signal, 
        connect_signal, 
        disconnect_signal
        )
from urwid import __version__ as urwid_version

from .. import __version__
from ..models import is_DM, get_authors_username
from ..utils import encode 
from .base import UserInterface
 
TWEET_MAX_CHARS = 140

banner = [ 
     "   _                             ",
     " _| |_ _   _ _ __ ___  ___  ____ ",
     "|_   _| | | | '__/ __|/   \/ ___|",
     "  | | | | | | |  |   \  _ ||   \\ ",
     "  | |_| |_| | |  \__ |  __/\__ | ",
     "  \___|\____|_| |____/\___||___/ ",
     "  ······························ ",
     "%s" % __version__,
     "",
     "",
     _("Press '?' for help"),
     _("Press 'q' to quit turses"),
     "",
]


class CursesInterface(Frame, UserInterface):
    """
    Creates a curses interface for the program, providing functions to draw 
    all the components of the UI.
    """

    def __init__(self):
        Frame.__init__(self,
                       WelcomeBuffer(),
                       header=TabsWidget(),
                       footer=StatusBar(''))
        self._editor_mode = False

    # -- Modes ----------------------------------------------------------------

    def draw_timelines(self, timelines):
        self.body = TimelinesBuffer(timelines)
        self.set_body(self.body)

    def show_info(self):
        self.header.clear()
        self.body = WelcomeBuffer()
        self.set_body(self.body)

    def show_help(self, configuration):
        self.clear_header()
        self.status_info_message(_('Type <Esc> to leave the help page.'))
        self.body = HelpBuffer(configuration)
        self.set_body(self.body)

    # -- Header ---------------------------------------------------------------

    def clear_header(self):
        self.header.clear()

    # -- Footer ---------------------------------------------------------------
        
    def status_message(self, text):
        if self.footer.__class__ is not StatusBar:
            return
        self.footer.message(text)
        self.set_footer(self.footer)

    def status_error_message(self, message):
        if self.footer.__class__ is not StatusBar:
            return
        self.footer.error_message(message)

    def status_info_message(self, message):
        if self.footer.__class__ is not StatusBar:
            return
        self.footer.info_message(message)

    def clear_status(self):
        self.footer = StatusBar()
        self.set_footer(self.footer)

    # -- Timeline mode --------------------------------------------------------

    def focus_timeline(self, index):
        """Give focus to the `index`-th visible timeline."""
        self.body.focus_timeline(index)

    def focus_status(self, index):
        if callable(getattr(self.body, 'set_focus', None)):
            self.body.set_focus(index)

    def set_tab_names(self, names):
        self.header.set_tabs(names)
        self.set_header(self.header)

    def activate_tab(self, index):
        self.header.set_active_tab(index)
        self.set_header(self.header)

    # -- Help mode ------------------------------------------------------------

    def focus_next(self):
        self.body.scroll_down()

    def focus_previous(self):
        self.body.scroll_up()

    def focus_first(self):
        self.body.scroll_top()

    def focus_last(self):
        self.body.scroll_bottom()

    # -- Editors --------------------------------------------------------------

    def _show_editor(self,
                     editor_cls,
                     prompt,
                     content,
                     done_signal_handler,
                     **kwargs):
        self.editor = editor_cls(prompt=prompt,
                                 content=content,
                                 done_signal_handler=done_signal_handler,
                                 **kwargs) 
        self.footer = self.editor
        self.set_footer(self.footer)
        self.set_focus('footer')

    def show_text_editor(self, 
                         prompt='', 
                         content='', 
                         done_signal_handler=None):
        self._show_editor(TextEditor,
                          prompt,
                          content,
                          done_signal_handler,)

    def show_tweet_editor(self, 
                          prompt='', 
                          content='', 
                          done_signal_handler=None):
        self._show_editor(TweetEditor,
                          prompt,
                          content,
                          done_signal_handler,)

    def show_dm_editor(self, 
                       prompt='', 
                       content='',
                       recipient='',
                       done_signal_handler=None):
        self._show_editor(DmEditor,
                          prompt,
                          content,
                          done_signal_handler,
                          recipient=recipient,)

    def remove_editor(self, done_signal_handler):
        disconnect_signal(self.editor, 'done', done_signal_handler)
        self.editor = None
        self.clear_status()


class WelcomeBuffer(WidgetWrap):
    """Displays information about the program."""

    # width, in columns, of the banner
    col_width = 30

    def __init__(self):
        self.text = []
        self.__super.__init__(self._create_text())

    def _create_text(self):
        """Creates the text to display in the welcome buffer."""
        self.text = []
        for line in banner:
            self._insert_line(line)

        return ScrollableListBox(self.text)

    def _insert_line(self, line):
        text= Text(line, align='center')
        self.text.append(text)
        

class TextEditor(WidgetWrap):
    """Editor for creating arbitrary text."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, 
                 prompt, 
                 content, 
                 done_signal_handler):
        if content:
            content += ' '
        self.editor = Edit(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)
        self.last_key = ''
        
        connect_signal(self, 'done', done_signal_handler)

        self.__super.__init__(self.editor)

    def keypress(self, size, key):
        if key == 'enter' and self.last_key == 'enter':
            self.emit_done_signal(self.editor.get_edit_text())
            return
        elif key == 'esc':
            self.emit_done_signal()
            return

        self.last_key = key
        size = size,
        self.editor.keypress(size, key)

    def emit_done_signal(self, content=None):
        emit_signal(self, 'done', content)


class TweetEditor(WidgetWrap):
    """Editor for creating tweets."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, 
                 prompt, 
                 content, 
                 done_signal_handler):
        if content:
            content += ' '
        self.editor = Edit(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)

        self.counter = len(content)
        self.counter_widget = Text(str(self.counter))

        widgets = [('fixed', 4, self.counter_widget), self.editor]
        w = Columns(widget_list=widgets,
                    # `Column` passes keypresses to the focused widget,
                    # in this case the editor
                    focus_column=1)

        connect_signal(self, 'done', done_signal_handler)
        connect_signal(self.editor, 'change', self.update_counter)

        self.__super.__init__(w)

    def update_counter(self, edit, new_edit_text):
        self.counter = len(new_edit_text)
        self.counter_widget.set_text(str(self.counter))

    def keypress(self, size, key):
        if key == 'enter' and self.last_key == 'enter':
            if self.counter > TWEET_MAX_CHARS:
                return
            else:
                self.emit_done_signal(self.editor.get_edit_text())
        elif key == 'esc':
            self.emit_done_signal()
            return

        self.last_key = key
        size = size,
        editor = self._w.get_focus()
        editor.keypress(size, key)

    def emit_done_signal(self, content=None):
        emit_signal(self, 'done', content)


class DmEditor(TweetEditor):
    """Editor for creating DMs."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, 
                 recipient, 
                 prompt, 
                 content, 
                 done_signal_handler):
        self.recipient = recipient
        TweetEditor.__init__(self, 
                             prompt='DM to %s' % recipient, 
                             content='',
                             done_signal_handler=done_signal_handler)
    
    def emit_done_signal(self, content=None):
        emit_signal(self, 'done', self.recipient, content)


class TabsWidget(WidgetWrap):
    """
    A widget that renders tabs with the given strings as titles.

    One of them is highlighted as the active tab.
    """

    def __init__(self, tabs=[]):
        """Creates tabs with the names given in `tabs`."""
        self.tabs = tabs
        if tabs:
            self.active_index = 0
            self.visible_indexes = [0]
        else:
            self.active_index = -1
            self.visible_indexes = []
        created_text = self._create_text()
        text = created_text if created_text else ''
        WidgetWrap.__init__(self, Text(text))

    def _is_valid_index(self, index):
        return index >= 0 and index < len(self.tabs)

    def _create_text(self):
        """Creates the text that is rendered as the tab list."""
        text = []
        for i, tab in enumerate(self.tabs):
            if i == self.active_index:
                text.append(('active_tab', u'│' + tab + u' '))
            elif i in self.visible_indexes:
                text.append(('visible_tab', u'│' + tab + u' '))
            else:
                text.append(('inactive_tab', u'│' + tab + u' '))
        return text

    def _update_text(self):
        text = self._create_text()
        self._w = Text(text)

    def append_tab(self, tab):
        self.tabs.append(unicode(tab))
        self._update_text()

    def delete_current_tab(self):
        del self.tabs[self.active_index]
        self._update_text()

    def set_active_tab(self, pos):
        self.active_index = pos
        self._update_text()

    def set_visible_tabs(self, indexes):
        self.visible_indexes = list(indexes)
        self._update_text()

    def set_tabs(self, tabs):
        self.tabs = tabs
        self._update_text()

    def clear(self):
        self._w.set_text('')


class StatusBar(WidgetWrap):
    """Displays text."""

    INFO = "[INFO]"
    ERROR = "[ERROR]"
    ARROW = " => "

    def __init__(self, text=''):
        WidgetWrap.__init__(self, Text(text))

    def message(self, text):
        """Write `text` on the footer.""" 
        self._w.set_text(text)

    def error_message(self, text):
        self.message([('error', self.ERROR),
                      ('default', self.ARROW + text),])

    def info_message(self, text):
        self.message([('info', self.INFO),
                      ('default', self.ARROW +  text),])

    def clear(self):
        """Clear the text."""
        self._w.set_text('')


class ScrollableListBox(ListBox):
    """
    A `ListBox` subclass with additional methods for scrolling the
    focus up and down, to the bottom and to the top.
    """
    def __init__(self, 
                 contents, 
                 offset=1):
        """
        Arguments:

        `contents` is a list with the elements contained in the 
        `ScrollableListBox`.

        `offset` is the number of position that `scroll_up` and `scroll_down`
        shift the cursor.
        """
        self.offset = offset

        ListBox.__init__(self, 
                         SimpleListWalker(contents))

    def focus_previous(self):
        """Sets the focus in the previous element (if any) of the listbox."""
        focus_status, pos = self.get_focus()
        if pos is None:
            return

        new_pos = pos - self.offset
        if new_pos < 0:
            new_pos = 0
        self.set_focus(new_pos)

    def focus_next(self):
        """Sets the focus in the next element (if any) of the listbox."""
        focus_status, pos = self.get_focus()
        if pos is None:
            return

        new_pos = pos + self.offset
        if new_pos >= len(self.body):
            new_pos = len(self.body) - 1
        self.set_focus(new_pos)

    def focus_first(self):
        """Sets the focus in the first element (if any) of the listbox."""
        if len(self.body):
            self.set_focus(0)

    def focus_last(self):
        """Sets the focus in the last element (if any) of the listbox."""
        last = len(self.body) - 1
        if last:
            self.set_focus(last)


class ScrollableListBoxWrapper(WidgetWrap):
    """
    """
    def __init__(self, contents=None):
        columns = [] if contents is None else contents
        WidgetWrap.__init__(self, columns)

    def scroll_up(self):
        self._w.focus_previous()

    def scroll_down(self):
        self._w.focus_next()

    def scroll_top(self):
        self._w.focus_first()

    def scroll_bottom(self):
        self._w.focus_last()


class HelpBuffer(ScrollableListBoxWrapper):
    """
    A widget that displays all the keybindings of the given configuration.
    """

    col = [30, 7]

    def __init__ (self, configuration):
        self.configuration = configuration
        
        self.items = []
        self.create_help_buffer()

        offset = int(len(self.items) / 2)
        ScrollableListBoxWrapper.__init__(self, 
                                          ScrollableListBox(self.items,
                                                            offset=offset,))

    def create_help_buffer(self):
        # TODO: remove the descriptions from the code. Store the keybindings
        #       in `turses/constant.py`. 
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
        self.insert_help_item('shift_buffer_beggining', _('Shift active buffer to the beggining'))
        self.insert_help_item('shift_buffer_end', _('Shift active buffer to the end'))
        self.insert_help_item('expand_visible_left', _('Expand visible timelines one column to the left'))
        self.insert_help_item('expand_visible_right', _('Expand visible timelines one column to the right'))
        self.insert_help_item('shrink_visible_left', _('Shrink visible timelines one column from the left'))
        self.insert_help_item('shrink_visible_right', _('Shrink visible timelines one column from the left'))
        self.insert_help_item('delete_buffer', _('Delete active buffer'))
        self.insert_help_item('clear', _('Clear active buffer'))
        self.insert_help_item('mark_all_as_read', _('Mark all tweets in timeline as read'))

        # Twitter
        self.insert_division(_('Tweets'))
        self.insert_help_item('tweet', _('Compose a tweet'))
        self.insert_help_item('delete_tweet', _('Delete selected tweet (must be yours)'))
        self.insert_help_item('reply', _('Reply to selected tweet'))
        self.insert_help_item('retweet', _('Retweet selected tweet'))
        self.insert_help_item('retweet_and_edit', _('Retweet selected tweet editing it first'))
        self.insert_help_item('sendDM', _('Send direct message'))
        self.insert_help_item('update', _('Refresh current timeline'))
        self.insert_help_item('tweet_hashtag', _('Compose a tweet with the same hashtags as the focused'))

        self.insert_division(_('Friendship'))
        self.insert_help_item('follow_selected', _('Follow selected tweet\'s author'))
        self.insert_help_item('unfollow_selected', _('Unfollow selected tweet\'s author'))

        self.insert_division(_('Favorites'))
        self.insert_help_item('fav', _('Mark selected tweet as favorite'))
        self.insert_help_item('delete_fav', _('Remove a tweet from favorites'))

        self.insert_division(_('Timelines'))
        self.insert_help_item('home', _('Go to home timeline'))
        self.insert_help_item('favorites', _('Go to favorites timeline'))
        self.insert_help_item('mentions', _('Go to mentions timeline'))
        self.insert_help_item('DMs', _('Go to direct message timeline'))
        self.insert_help_item('search', _('Search for term and show resulting timeline'))
        self.insert_help_item('search_user', _('Show somebody\'s public timeline'))
        self.insert_help_item('search_myself', _('Show your public timeline'))
        self.insert_help_item('hashtags', _('Search the hashtags of the focused status'))
        self.insert_help_item('thread', _('Open selected thread'))
        self.insert_help_item('user_info', _('Show user information '))
        self.insert_help_item('help', _('Show help buffer'))

        # Others
        self.insert_division(_('Others'))
        self.insert_help_item('quit', _('Leave turses'))
        self.insert_help_item('openurl', _('Open URL in browser'))
        self.insert_help_item('open_image', _('Open image'))
        self.insert_help_item('redraw', _('Redraw the screen'))

    def insert_header(self):
        widgets = [
            ('fixed', self.col[0], Text('  Name')),
            ('fixed', self.col[1], Text('Key')),
            Text('Description') 
        ]
        self.items.append(Columns(widgets))

    def insert_division(self, title):
        self.items.append(Divider(' '))
        self.items.append(Padding(AttrWrap(Text(title), 'focus'), left=4))
        self.items.append(Divider(' '))

    def insert_help_item(self, key, description):
        widgets = [
            ('fixed', self.col[0], Text('  ' + key)), 
            ('fixed', self.col[1], Text(self.configuration.keys[key])),
            Text(description) 
        ]
        self.items.append(Columns(widgets))

    # from `ScrollableListBoxWrapper`

    def scroll_up(self):
        self._w.focus_previous()

    def scroll_down(self):
        self._w.focus_next()

    def scroll_top(self):
        self._w.focus_first()


class TimelinesBuffer(WidgetWrap):
    """A widget that displays one or more `Timeline` objects."""

    def __init__(self, timelines=None):
        if timelines:
            timeline_widgets = [TimelineWidget(timeline) for timeline in timelines]
        else:
            timeline_widgets = []
        WidgetWrap.__init__(self, Columns(timeline_widgets))

    def scroll_up(self):
        active_widget = self._w.get_focus()
        active_widget.focus_previous()

    def scroll_down(self):
        active_widget = self._w.get_focus()
        active_widget.focus_next()

    def scroll_top(self):
        active_widget = self._w.get_focus()
        active_widget.focus_first()

    def scroll_bottom(self):
        active_widget = self._w.get_focus()
        active_widget.focus_last()

    def clear(self):
        """Clears the buffer."""
        # FIXME
        pass

    def render_timelines(self, timelines):
        """Renders the given statuses."""
        timeline_widgets = [TimelineWidget(timeline) for timeline in timelines]
        self._w = Columns(timeline_widgets) 

    def set_focus(self, index):
        active_widget = self._w.get_focus()
        active_widget.set_focus(index)

    def focus_timeline(self, index):
        self._w.set_focus_column(index)


class TimelineWidget(ScrollableListBox):
    """
    A `ListBox` containing a list of Twitter statuses, each of which is
    rendered as a `StatusWidget`.
    """

    def __init__(self, timeline=None):
        statuses = timeline if timeline else []
        status_widgets = [StatusWidget(status) for status in statuses]
        ScrollableListBox.__init__(self, status_widgets)


class StatusWidget(WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__ (self, status):
        self.status = status
        text = status.text
        status_content = Padding(AttrWrap(Text(text), 'body'), left=1, right=1)
        header = self._create_header(status)
        box = BoxDecoration(status_content, title=header)
        if not is_DM(status) and status.is_favorite:
            widget = AttrWrap(box, 'favorited', 'focus')
        else:
            widget = AttrWrap(box, 'line', 'focus')
        self.__super.__init__(widget)

    def selectable(self):
        return True

    def keypress(self, size, key):
        #TODO! modify widget attributes in response to certain actions
        return key

    def _create_header(self, status):
        """Return the header text for the status associated with this widget."""
        if is_DM(status):
            return self._dm_header(status)

        # tweet or retweet
        reply = ''
        retweeted = ''
        retweet_count = ''
        retweeter = ''
        username = status.user
        relative_created_at = status.get_relative_created_at()

        # reply
        if status.is_reply:
            reply = u' \u2709'

        # retweet
        if status.is_retweet:
            retweeted = u" \u267b "
            retweeter = username
            author = get_authors_username(status)
            username = author 
            retweet_count = str(status.retweet_count)
            
        # create header
        header_template = ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} '
        header = unicode(header_template).format(
            username= username,
            retweeted = retweeted,
            retweeter = retweeter,
            time = relative_created_at,
            reply = reply,
            retweet_count = retweet_count,
        )

        return encode(header)

    def _dm_header(self, dm):
        # TODO: make DM template configurable
        dm_template = ' {sender_screen_name} -> {recipient_screen_name} - {time} '
        relative_created_at = dm.get_relative_created_at()
        header = unicode(dm_template).format(
            sender_screen_name=dm.sender_screen_name,
            recipient_screen_name=dm.recipient_screen_name,
            time = relative_created_at,
        )

        return encode(header)


class BoxDecoration(WidgetDecoration, WidgetWrap):
    """Draw a box around `original_widget`."""

    def __init__(self, original_widget, title=''):
        self.color = 'header'
        if int(urwid_version[0]) == 1:
            utf8decode = lambda string: string

        def use_attr(a, t):
            if a:
                t = AttrWrap(t, a)
            return t

        # top line
        tline = None
        tline_attr = Columns([('fixed', 2, 
                                        Divider(utf8decode("─"))),
                                    ('fixed', len(title), 
                                        AttrWrap(Text(title), self.color)),
                                    Divider(utf8decode("─")),])
        tline = use_attr(tline, tline_attr)
        # bottom line
        bline = None
        bline = use_attr(bline, Divider(utf8decode("─")))
        # left line
        lline = None
        lline = use_attr(lline, SolidFill(utf8decode("│")))
        # right line
        rline = None
        rline = use_attr(rline, SolidFill(utf8decode("│")))
        # top left corner
        tlcorner = None
        tlcorner = use_attr(tlcorner, Text(utf8decode("┌")))
        # top right corner
        trcorner = None
        trcorner = use_attr(trcorner, Text(utf8decode("┐")))
        # bottom left corner
        blcorner = None
        blcorner = use_attr(blcorner, Text(utf8decode("└")))
        # bottom right corner
        brcorner = None
        brcorner = use_attr(brcorner, Text(utf8decode("┘")))

        # top
        top = Columns([('fixed', 1, tlcorner),
                             tline, 
                             ('fixed', 1, trcorner),])
        # middle
        middle = Columns([('fixed', 1, lline),
                                original_widget, 
                                ('fixed', 1, rline)], 
                               box_columns = [0,2], 
                               focus_column = 1)
        # bottom
        bottom = Columns([('fixed', 1, blcorner),
                                bline, 
                                ('fixed', 1, brcorner)])

        # widget decoration
        pile = Pile([('flow',top),
                           middle,
                           ('flow',bottom)], 
                          focus_item = 1)

        WidgetDecoration.__init__(self, original_widget)
        WidgetWrap.__init__(self, pile)
