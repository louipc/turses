# -*- coding: utf-8 -*-

"""
turses.ui
~~~~~~~~~

This module contains the UI widgets.
"""

from gettext import gettext as _

from urwid import (
        AttrMap,
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

from turses import version
from turses.config import (
        MOTION_KEY_BINDINGS,
        BUFFERS_KEY_BINDINGS,
        TWEETS_KEY_BINDINGS,
        TIMELINES_KEY_BINDINGS,
        META_KEY_BINDINGS,
        TURSES_KEY_BINDINGS,
        
        CONFIG_PATH
)
from turses.models import (
        is_hashtag, 
        is_username, 
        is_DM, 
        
        get_authors_username, 
        sanitize_username
)
from turses.utils import encode 
 
TWEET_MAX_CHARS = 140

BANNER = [ 
     "   _                             ",
     " _| |_ _   _ _ __ ___  ___  ____ ",
     "|_   _| | | | '__/ __|/   \/ ___|",
     "  | | | | | | |  |   \  ~ ||   \\ ",
     "  | |_| |_| | |  \__ |  __/\__ | ",
     "  \___|\____|_| |____/\___||___/ ",
     "  ······························ ",
     "%s" % version,
     "",
     "",
     _("Press '?' for help"),
     _("Press 'q' to quit turses"),
     "",
     "",
     _("New configuration and token files from the old ones"),
     _("have been created in %s." % CONFIG_PATH),
     "",
     "",
     "    ~                                              ",
     "    |+.turses/                                     ",
     "    | |-config                                     ",
     _("    | |-token       # default account's token      "),
     _("    | `-bob.token   # another account's token      "),
     "    |+...                                          ",
     "    |-...                                          ",
     "",
     "",
]


class CursesInterface(Frame):
    """
    Creates a curses interface for the program, providing functions to draw 
    all the components of the UI.
    """

    def __init__(self,
                 configuration):
        Frame.__init__(self,
                       WelcomeBuffer(),
                       header=TabsWidget(),
                       footer=StatusBar(''))
        self._configuration = configuration
        self._editor_mode = False

    # -- Modes ----------------------------------------------------------------

    def draw_timelines(self, timelines):
        self.body = TimelinesBuffer(timelines, 
                                    configuration=self._configuration)
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
        
    def _visible_status_bar(self):
        return self.footer.__class__ is StatusBar

    def _can_write_status(self):
        if self.footer is None:
            self.footer = StatusBar()
        elif self._visible_status_bar():
            pass
        else:
            return False
        return True

    def status_message(self, text):
        if self._can_write_status():
            self.footer.message(text)
            self.set_footer(self.footer)

    def status_error_message(self, message):
        if self._can_write_status():
            self.footer.error_message(message)

    def status_info_message(self, message):
        if self._can_write_status():
            self.footer.info_message(message)

    def clear_status(self):
        self.footer = None
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
        try:
            disconnect_signal(self.editor, 'done', done_signal_handler)
        except:
            # `disconnect_signal` raises an exception if no signal was
            # connected from `self.editor`. We can safely ignore it.
            pass
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
        for line in BANNER:
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

        widgets = [self.editor]
        w = AttrMap(Columns(widgets), 'editor')

        connect_signal(self, 'done', done_signal_handler)

        self.__super.__init__(w)

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
        w = AttrMap(Columns(widgets), 'editor')

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
        self.editor.keypress(size, key)

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

    def _insert_bindings(self, bindings):
        for label in bindings:
            values = self.configuration.key_bindings[label]
            key, description = values[0], values[1]
            widgets = [
                ('fixed', self.col[0], Text('  ' + label)), 
                ('fixed', self.col[1], Text(key)),
                Text(description) 
            ]
            self.items.append(Columns(widgets))

    def create_help_buffer(self):
        self.insert_header()

        self.insert_title(_('Motion'))
        self._insert_bindings(MOTION_KEY_BINDINGS)

        self.insert_title(_('Buffers'))
        self._insert_bindings(BUFFERS_KEY_BINDINGS)

        self.insert_title(_('Tweets'))
        self._insert_bindings(TWEETS_KEY_BINDINGS)

        self.insert_title(_('Timelines'))
        self._insert_bindings(TIMELINES_KEY_BINDINGS)

        self.insert_title(_('Meta'))
        self._insert_bindings(META_KEY_BINDINGS)

        self.insert_title(_('Turses'))
        self._insert_bindings(TURSES_KEY_BINDINGS)

    def insert_header(self):
        widgets = [
            ('fixed', self.col[0], Text('  Name')),
            ('fixed', self.col[1], Text('Key')),
            Text('Description') 
        ]
        self.items.append(Columns(widgets))

    def insert_title(self, title):
        self.items.append(Divider(' '))
        self.items.append(Padding(AttrMap(Text(title), 'focus'), left=4))

    # from `ScrollableListBoxWrapper`

    def scroll_up(self):
        self._w.focus_previous()

    def scroll_down(self):
        self._w.focus_next()

    def scroll_top(self):
        self._w.focus_first()


class TimelinesBuffer(WidgetWrap):
    """A widget that displays one or more `Timeline` objects."""

    def __init__(self, timelines=None, **kwargs):
        if timelines:
            timeline_widgets = [TimelineWidget(timeline, **kwargs) for timeline in timelines]
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

    def __init__(self, timeline=None, configuration=None):
        statuses = timeline if timeline else []
        status_widgets = [StatusWidget(status, configuration) for status in statuses]
        ScrollableListBox.__init__(self, status_widgets)


class StatusWidget(WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__ (self, status, configuration):
        self.status = status
        self.configuration = configuration

        text = self.apply_attributes(status.text)
        status_content = Padding(AttrMap(Text(text), 'body'), left=1, right=1)
        header = self._create_header(status)
        box = BoxDecoration(status_content, title=header)

        if not is_DM(status) and status.is_favorite:
            widget = AttrMap(box, 'favorited', 'focus')
        else:
            widget = AttrMap(box, 'line', 'focus')
        self.__super.__init__(widget)

    def apply_attributes(self, text):
        """
        Apply the attributes to certain words of `text`. Right now it applies
        attributes to hashtags and Twitter usernames.
        """
        words = text.split()
        def apply_attribute(string):
            if is_hashtag(string):
                return ('hashtag', string)
            elif string.startswith('@') and is_username(string[1:-1]):
                # we can lose some characters here..
                username = sanitize_username(string)
                return ('attag', '@' + username)
            else:
                return  string
        text = map(apply_attribute, words)
        tweet = []
        for word in text:
            tweet.append(word)
            tweet.append(' ')
        return tweet

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
        header_template = ' ' + self.configuration.styles['header_template'] + ' '
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
        dm_template = ' ' + self.configuration.styles['dm_template'] + ' '
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

        def use_attr(a, t):
            if a:
                t = AttrMap(t, a)
            return t

        # top line
        tline = None
        tline_attr = Columns([('fixed', 2, 
                                        Divider(u"─")),
                                    ('fixed', len(title), 
                                        AttrMap(Text(title), self.color)),
                                    Divider(u"─"),])
        tline = use_attr(tline, tline_attr)
        # bottom line
        bline = None
        bline = use_attr(bline, Divider(u"─"))
        # left line
        lline = None
        lline = use_attr(lline, SolidFill(u"│"))
        # right line
        rline = None
        rline = use_attr(rline, SolidFill(u"│"))
        # top left corner
        tlcorner = None
        tlcorner = use_attr(tlcorner, Text(u"┌"))
        # top right corner
        trcorner = None
        trcorner = use_attr(trcorner, Text(u"┐"))
        # bottom left corner
        blcorner = None
        blcorner = use_attr(blcorner, Text(u"└"))
        # bottom right corner
        brcorner = None
        brcorner = use_attr(brcorner, Text(u"┘"))

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
