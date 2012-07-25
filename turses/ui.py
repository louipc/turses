# -*- coding: utf-8 -*-

"""
This module contains the curses UI widgets.
"""

import logging
from gettext import gettext as _

from urwid import (AttrMap, WidgetWrap, Padding, Divider, SolidFill,
                   WidgetDecoration, LineBox, Filler,

                   # widgets
                   Text, Edit, Frame, Columns, Pile, ListBox, SimpleListWalker,
                   Overlay,

                   # signals
                   signals, emit_signal, connect_signal, disconnect_signal)

from turses import version
from turses.config import (MOTION_KEY_BINDINGS, BUFFERS_KEY_BINDINGS,
                           TWEETS_KEY_BINDINGS, TIMELINES_KEY_BINDINGS,
                           META_KEY_BINDINGS, TURSES_KEY_BINDINGS,

                           configuration)
from turses.models import is_DM, TWEET_MAXIMUM_CHARACTERS
from turses.utils import encode, is_hashtag, is_username, is_url


# - Text parsing --------------------------------------------------------------

def apply_attribute(string,
                    hashtag='hashtag',
                    attag='attag',
                    url='url'):
    """
    Apply an attribute to `string` dependending on wether it is
    a hashtag, a Twitter username or an URL.

    >>> apply_attribute('#Python')
    ('hashtag', u'#Python')
    >>> apply_attribute('@dialelo')
    ('attag', u'@dialelo')
    >>> apply_attribute('@dialelo',
                        attag='username')
    ('username', u'@dialelo')
    >>> apply_attribute('http://www.dialelo.com')
    ('url', u'http://www.dialelo.com')
    >>> apply_attribute('turses')
    u'turses'
    """
    string = unicode(string)

    if is_hashtag(string):
        return (hashtag, string)
    elif string.startswith('@') and is_username(string[1:]):
        return (attag, string)
    elif is_url(string):
        return  (url, string)
    else:
        return string


def parse_attributes(text,
                     hashtag='hashtag',
                     attag='attag',
                     url='url'):
    """
    Parse the attributes in `text` and isolate the hashtags, usernames
    and URLs with the provided attributes.

    >>> text = 'I love #Python'
    >>> parse_attributes(text=text,
    ...                  hashtag='hashtag')
    ['I love ', ('hashtag', '#Python')]
    """

    # nothing to do
    if not text:
        return u''

    words = text.split()
    parsed_text = [apply_attribute(word) for word in words]

    def add_withespace(parsed_word):
        if isinstance(parsed_word, tuple):
            # is an (attr, word) tuple
            return parsed_word
        else:
            return parsed_word + ' '

    tweet = [add_withespace(parsed_word) for parsed_word
                                         in parsed_text]

    # insert spaces after an attribute
    indices = []
    for i, word in enumerate(tweet[:-1]):
        word_is_attribute = isinstance(word, tuple)

        if word_is_attribute:
            indices.append(i + 1 + len(indices))

    for index in indices:
        tweet.insert(index, u' ')

    # remove trailing withespace
    if tweet and isinstance(tweet[-1], basestring):
        tweet[-1] = tweet[-1][:-1]

    return tweet

def extract_attributes(entities, hashtag, attag, url):
    """
    Extract attributes from entities.

    Return a list with (`attr`, string[, replacement]) tuples for each
    entity in the status.
    """
    def map_attr(attr, entity_list):
        """
        Return a list with (`attr`, string) tuples for each string in
        `entity_list`.
        """
        url_format = configuration.styles['url_format']
        attributes = []
        for entity in entity_list:
            # urls are a special case, we change the URL shortened by
            # Twitter (`http://t.co/*`) by the URL returned in
            # `display_url`
            indices = entity.get('indices')
            is_url = entity.get('display_url', False)

            if is_url:
                # `display_url` is the default
                url = entity.get('display_url')
                if url_format == 'shortened':
                    url = entity.get('url')
                elif url_format == 'original' and 'expanded_url' in entity:
                    url = entity.get('expanded_url')
                mapping = (attr, indices, url)
            else:
                mapping = (attr, indices)
            attributes.append(mapping)
        return attributes

    entity_names_and_attributes = [
        ('user_mentions', attag),
        ('hashtags', hashtag),
        ('urls', url),
        ('media', url),
    ]

    attributes = []
    for entity_name, entity_attribute in entity_names_and_attributes:
        entity_list = entities.get(entity_name, [])
        attributes.extend(map_attr(entity_attribute, entity_list))

    # sort mappings to split the text in order
    attributes.sort(key=lambda mapping: mapping[1][0])

    return attributes

def map_attributes(status, hashtag, attag, url):
    """
    Return a list of strings and tuples for hashtag, attag and
    url entities.

    For a hashtag, its tuple would be (`hashtag`, text).

    >>> from datetime import datetime
    >>> s = Status(id=0,
    ...            created_at=datetime.now(),
    ...            user='dialelo',
    ...            text='I love #Python',)
    >>> map_attributes(s, 'hashtag', 'attag', 'url')
    ['I love ', ('hashtag', '#Python')]
    """
    is_retweet = getattr(status, 'is_retweet', False)

    if is_retweet:
        # call this method on the retweeted status
        return map_attributes(status.retweeted_status, hashtag, attag, url)

    if not status.entities:
        # no entities defined, parse text *manually*
        #  - Favorites don't include any entities at the time of writing
        text = status.retweeted_status.text if is_retweet else status.text
        return parse_attributes(text, hashtag, attag, url)

    # we have entities, extract the (attr, string[, replacement]) tuples
    assert status.entities
    attribute_mappings = extract_attributes(entities=status.entities,
                                            hashtag=hashtag,
                                            attag=attag,
                                            url=url)

    text = []
    status_text = unicode(status.text)
    # start from the beggining
    index = 0
    for mapping in attribute_mappings:
        attribute = mapping[0]
        starts, ends = mapping[1]

        # this text has an attribute associated
        entity_text = status_text[starts:ends]

        if attribute == url and len(mapping) == 3:
            ## if the text is a url and a third element is included in the
            ## tuple; the third element is the original URL
            entity_text = mapping[2]

        # append normal text before the text with an attribute
        normal_text = status_text[index:starts]
        if normal_text:
            text.append(normal_text)

        # append text with attribute
        text_with_attribute = (attribute, entity_text)
        text.append(text_with_attribute)

        # update index, continue from where the attribute text ends
        index = ends

    # after parsing all attributes we can have some text left
    normal_text = status_text[index:]
    if normal_text:
        text.append(normal_text)

    return text



# - Main UI -------------------------------------------------------------------



class CursesInterface(WidgetWrap):
    """
    Creates a curses interface for the program, providing functions to draw
    all the components of the UI.
    """

    def __init__(self):
        self._editor = None

        # header
        header = TabsWidget()

        # body
        body = Banner()

        # footer
        self._status_bar = configuration.styles.get('status_bar', False)
        if self._status_bar:
            footer = StatusBar('')
        else:
            footer = None

        self.frame = Frame(body,
                           header=header,
                           footer=footer)

        WidgetWrap.__init__(self, self.frame)

    def _build_overlay_widget(self,
                              top_w,
                              align,
                              width,
                              valign,
                              height,
                              min_width,
                              min_height):
        return Overlay(top_w=Filler(top_w),
                       bottom_w=self.frame,
                       align=align,
                       width=width,
                       valign=valign,
                       height=height,
                       min_width=width,
                       min_height=height)

    # -- Modes ----------------------------------------------------------------

    def draw_timelines(self, timelines):
        self.frame.body = TimelinesBuffer(timelines)
        self.frame.set_body(self.frame.body)

    def show_info(self):
        self.frame.header.clear()
        self.frame.body = Banner()
        self.frame.set_body(self.frame.body)

    def show_help(self):
        self.clear_header()
        self.status_info_message(_('type <esc> to leave the help page.'))
        self.frame.body = HelpBuffer()
        self.frame.set_body(self.frame.body)

    # -- Header ---------------------------------------------------------------

    def clear_header(self):
        self.frame.header.clear()

    def set_tab_names(self, names):
        self.frame.header.set_tabs(names)
        self.frame.set_header(self.frame.header)

    def activate_tab(self, index):
        self.frame.header.set_active_tab(index)
        self.frame.set_header(self.frame.header)

    def highlight_tabs(self, indexes):
        self.frame.header.set_visible_tabs(indexes)

    # -- Footer ---------------------------------------------------------------

    @property
    def can_write_status(self):
        if self._status_bar:
            if self.frame.footer is None:
                self.frame.footer = StatusBar('')
            return True
        return False

    def status_message(self, text):
        if self.can_write_status:
            self.frame.footer.message(text)
            self.frame.set_footer(self.frame.footer)

    def status_error_message(self, message):
        if self.can_write_status:
            self.frame.footer.error_message(message)

    def status_info_message(self, message):
        if self.can_write_status:
            self.frame.footer.info_message(message)

    def clear_status(self):
        self.frame.footer = None
        self.frame.set_footer(self.frame.footer)

    # -- Timeline mode --------------------------------------------------------

    def focus_timeline(self, index):
        """Give focus to the `index`-th visible timeline."""
        self.frame.body.focus_timeline(index)

    def focus_status(self, index):
        if callable(getattr(self.frame.body, 'set_focus', None)):
            self.frame.body.set_focus(index)

    def center_focus(self):
        if callable(getattr(self.frame.body, 'set_focus_valign', None)):
            logging.debug('centering focus')
            self.frame.body.set_focus_valign('middle')

    # -- motions --------------------------------------------------------------

    def focus_next(self):
        self.frame.body.scroll_down()

    def focus_previous(self):
        self.frame.body.scroll_up()

    def focus_first(self):
        self.frame.body.scroll_top()

    def focus_last(self):
        self.frame.body.scroll_bottom()

    # -- editors --------------------------------------------------------------

    def _show_editor(self,
                     editor_cls,
                     prompt,
                     content,
                     done_signal_handler,
                     **kwargs):
        self._editor = editor_cls(prompt=prompt,
                                  content=content,
                                  done_signal_handler=done_signal_handler,
                                  **kwargs)

        styles = configuration.styles
        horizontal_align = styles['editor_horizontal_align']
        vertical_align = styles['editor_vertical_align']

        self.show_widget_on_top(widget=self._editor,
                                width=80,
                                height=5,
                                align=horizontal_align,
                                valign=vertical_align,
                                min_height=5,)
        return self._editor

    def show_text_editor(self,
                         prompt='',
                         content='',
                         done_signal_handler=None,
                         cursor_position=None):
        return self._show_editor(TextEditor,
                                 prompt,
                                 content,
                                 done_signal_handler,
                                 cursor_position=cursor_position)

    def show_tweet_editor(self,
                          prompt='',
                          content='',
                          done_signal_handler=None,
                          cursor_position=None):
        return self._show_editor(TweetEditor,
                                 prompt,
                                 content,
                                 done_signal_handler,
                                 cursor_position=cursor_position)

    def show_dm_editor(self,
                       prompt='',
                       content='',
                       recipient='',
                       done_signal_handler=None):
        return self._show_editor(DmEditor,
                                 prompt,
                                 content,
                                 done_signal_handler,
                                 recipient=recipient,)

    def hide_editor(self, done_signal_handler):
        try:
            disconnect_signal(self._editor, 'done', done_signal_handler)
        except Exception, message:
            # `disconnect_signal` raises an exception if no signal was
            # connected from `self._editor`. we can safely ignore it.
            logging.exception(message)
        self._editor = None
        self.hide_widget_on_top()

    # - pop ups ---------------------------------------------------------------

    def show_user_info(self, user):
        widget = UserInfo(user)

        self.show_widget_on_top(widget, width=40, height=18)

    def hide_user_info(self):
        self.hide_widget_on_top()

    def show_widget_on_top(self,
                           widget,
                           width,
                           height,
                           align='center',
                           valign='middle',
                           min_height=0,
                           min_width=0):
        """Show `widget` on top of :attr:`frame`."""
        self._w = self._build_overlay_widget(top_w=widget,
                                             align=align,
                                             width=width,
                                             valign=valign,
                                             height=height,
                                             min_width=min_width,
                                             min_height=min_height)

    def hide_widget_on_top(self):
        """Hide the topmost widget (if any)."""
        self._w = self.frame


# - Program info --------------------------------------------------------------


class Banner(WidgetWrap):
    """Displays information about the program."""

    def __init__(self):
        self.text = []

        help_key = configuration.key_bindings['help'][0]
        quit_key = configuration.key_bindings['quit'][0]
        self.BANNER = [
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
             _("Press '%s' for help") % help_key,
             _("Press '%s' to quit turses") % quit_key,
             "",
             "",
             _("Configuration and token files reside under"),
             _("your $HOME directory"),
             #"",
             "",
             "    ~                                              ",
             "    |+.turses/                                     ",
             "    | |-config                                     ",
             _("    | |-token       # default account's token      "),
             _("    | `-bob.token   # another account's token      "),
             "    |+...                                          ",
             "",
             "",
        ]
        self.__super.__init__(self._create_text())

    def _create_text(self):
        """Create the text to display in the welcome buffer."""
        self.text = []
        for line in self.BANNER:
            self._insert_line(line)

        return ScrollableListBox(self.text)

    def _insert_line(self, line):
        text = Text(line, align='center')
        self.text.append(text)


# - Editors -------------------------------------------------------------------


class BaseEditor(WidgetWrap):
    """Base class for editors."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self,
                 prompt,
                 content,
                 done_signal_handler,
                 cursor_position=None):
        """
        Initializes editor, connects 'done' signal.

        When pressing 'enter' twice the `submit` method is called, which by
        default calls `emit_done_signal` with the text that has been
        introduced.

        When pressing 'esc' the `cancel` method is called, which by default
        calls `emit_done_signal` with no arguments.

        The subclasses must call the `_wrap` method with the editor widgets
        and `BaseEditor` will wrap it in a `urwid.Colums` widget, calling to
        `urwid.WidgetWrap.__init__` with the wrapped widget.
        """
        caption = _(u'%s (twice enter key to validate or esc) \n>> ') % prompt
        if content:
            content += ' '
        self.content = content
        self.editor = Edit(caption=caption,
                           edit_text=content,
                           edit_pos=cursor_position)
        self.last_key = None

        connect_signal(self, 'done', done_signal_handler)

    def _wrap(self, widgets):
        widgets = widgets if isinstance(widgets, list) else [widgets]
        composed_widget = Columns(widgets)

        widget = AttrMap(LineBox(composed_widget), 'editor')
        WidgetWrap.__init__(self, widget)

    def keypress(self, size, key):
        if key == 'enter' and self.last_key == 'enter':
            self.submit()
            return
        elif key == 'esc':
            self.cancel()
            return

        self.last_key = key
        size = size,
        self.editor.keypress(size, key)

    def submit(self):
        self.emit_done_signal(self.editor.get_edit_text())

    def cancel(self):
        self.emit_done_signal()

    def emit_done_signal(self, content=None):
        emit_signal(self, 'done', content)


class TextEditor(BaseEditor):
    """Editor for creating arbitrary text."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self,
                 prompt,
                 content,
                 done_signal_handler,
                 cursor_position=None):
        BaseEditor.__init__(self,
                            prompt,
                            content,
                            done_signal_handler,
                            cursor_position)

        self._wrap(self.editor)


class TweetEditor(BaseEditor):
    """Editor for creating tweets."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self,
                 prompt,
                 content,
                 done_signal_handler,
                 cursor_position=None):
        BaseEditor.__init__(self,
                            prompt,
                            content,
                            done_signal_handler,
                            cursor_position)

        self.counter = len(self.content)
        self.counter_widget = Text(str(self.counter))

        connect_signal(self.editor, 'change', self.update_counter)

        widgets = [('fixed', 4, self.counter_widget), self.editor]
        self._wrap(widgets)

    def update_counter(self, edit, new_edit_text):
        self.counter = len(new_edit_text)
        self.counter_widget.set_text(str(self.counter))

    def submit(self):
        if self.counter > TWEET_MAXIMUM_CHARACTERS:
            return
        else:
            self.emit_done_signal(self.editor.get_edit_text())


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


# - Header and footer ---------------------------------------------------------


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
                      ('default', self.ARROW + text)])

    def info_message(self, text):
        self.message([('info', self.INFO),
                      ('default', self.ARROW + text)])

    def clear(self):
        """Clear the text."""
        self._w.set_text('')


# - Base list widgets ---------------------------------------------------------


class Scrollable:
    """A interface that makes widgets *scrollable*."""
    def scroll_up(self):
        raise NotImplementedError

    def scroll_down(self):
        raise NotImplementedError

    def scroll_top(self):
        raise NotImplementedError

    def scroll_bottom(self):
        raise NotImplementedError


class ScrollableListBox(ListBox, Scrollable):
    """
    A ``urwid.ListBox`` subclass that implements the
    :class:`~turses.ui.Scrollable` interface.
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

    def scroll_up(self):
        focus_status, pos = self.get_focus()
        if pos is None:
            return

        new_pos = pos - self.offset
        if new_pos < 0:
            new_pos = 0
        self.set_focus(new_pos)

    def scroll_down(self):
        focus_status, pos = self.get_focus()
        if pos is None:
            return

        new_pos = pos + self.offset
        if new_pos >= len(self.body):
            new_pos = len(self.body) - 1
        self.set_focus(new_pos)

    def scroll_top(self):
        if len(self.body):
            self.set_focus(0)

    def scroll_bottom(self):
        last = len(self.body) - 1
        if last:
            self.set_focus(last)


class ScrollableWidgetWrap(WidgetWrap, Scrollable):
    """
    A ``urwid.WidgetWrap`` for :class:`~turses.ui.Scrollable`, list-like
    widgets.
    """
    def __init__(self, contents=None):
        columns = [] if contents is None else contents
        WidgetWrap.__init__(self, columns)

    def scroll_up(self):
        self._w.scroll_up()

    def scroll_down(self):
        self._w.scroll_down()

    def scroll_top(self):
        self._w.scroll_top()

    def scroll_bottom(self):
        self._w.scroll_bottom()


# - Help ----------------------------------------------------------------------


class HelpBuffer(ScrollableWidgetWrap):
    """
    A widget that displays all the keybindings of the given configuration.
    """

    col = [30, 7]

    def __init__(self):
        self.items = []
        self.create_help_buffer()

        offset = int(len(self.items) / 5)
        ScrollableWidgetWrap.__init__(self,
                                      ScrollableListBox(self.items,
                                                        offset=offset,))

    def _insert_bindings(self, bindings):
        for label in bindings:
            values = configuration.key_bindings[label]
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
            ('fixed', self.col[0], Text(_('  NAME'))),
            ('fixed', self.col[1], Text(_('KEY'))),
            Text(_('DESCRIPTION')),
        ]
        self.items.append(Columns(widgets))
        self.items.append(Divider('·'))

    def insert_title(self, title):
        self.items.append(Divider(' '))
        self.items.append(Padding(AttrMap(Text(title), 'focus'), left=4))


# - Timelines -----------------------------------------------------------------


class TimelinesBuffer(ScrollableWidgetWrap):
    """
    A widget that displays one or more `Timeline` objects.

    Another widget can be placed on top of it.
    """

    def __init__(self, timelines=None, **kwargs):
        timelines = [] if timelines is None else timelines

        widget = self._build_widget(timelines, **kwargs)

        ScrollableWidgetWrap.__init__(self, widget)

    def _build_widget(self, timelines, **kwargs):
        timeline_widgets = [TimelineWidget(timeline, **kwargs) for timeline
                                                                in timelines]
        return Columns(timeline_widgets)

    def render_timelines(self, timelines, **kwargs):
        """Render the given statuses."""
        self._w = self._build_widget(timelines, **kwargs)

    @property
    def columns(self):
        """
        The `Columns` widget.
        """
        return self._w

    @property
    def active_widget(self):
        """
        The active widget.
        """
        return self.columns.get_focus()

    def scroll_up(self):
        self.active_widget.scroll_up()

    def scroll_down(self):
        self.active_widget.scroll_down()

    def scroll_top(self):
        self.active_widget.scroll_top()

    def scroll_bottom(self):
        self.active_widget.scroll_bottom()

    def clear(self):
        """Clears the buffer."""
        # TODO
        pass

    def set_focus(self, index):
        self.active_widget.set_focus(index)

    def set_focus_valign(self, valign):
        self.active_widget.set_focus_valign(valign)

    def focus_timeline(self, index):
        self.columns.set_focus_column(index)

    # XXX:
    #  All keypresses are ignored so `turses.core.KeyHandler` can handle
    #  every keystroke. I tried to filter the input in `urwid`s `MainLoop`
    #  but did not work as expected.
    def keypress(self, size, key):
        return key


class TimelineWidget(ScrollableListBox):
    """
    A :class:`ScrollableListBox` containing a list of Twitter statuses, each of
    which is rendered as a :class:`StatusWidget`.
    """

    def __init__(self, timeline=None):
        statuses = timeline if timeline else []
        status_widgets = [StatusWidget(status) for status in statuses]
        ScrollableListBox.__init__(self, status_widgets)


class StatusWidget(WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__(self, status):
        self.status = status

        header_text = self._create_header(status)
        text = map_attributes(status,
                              hashtag='hashtag',
                              attag='attag',
                              url='url')

        is_favorite = not is_DM(status) and status.is_favorite
        widget = self._build_widget(header_text, text, is_favorite)

        self.__super.__init__(widget)

    def _build_widget(self, header_text, text, favorite=False):
        """Return the wrapped widget."""
        box_around_status = configuration.styles.get('box_around_status',
                                                          True)
        divider = configuration.styles.get('status_divider', False)

        header = AttrMap(Text(header_text), 'header')
        body = Padding(AttrMap(Text(text), 'body'), left=1, right=1)

        border_attr = 'line'
        if favorite:
            border_attr = 'favorited'

        if box_around_status:
            # draw a box around the status
            # focusing the first item both dividers are highlighted
            # on focus
            widget = AttrMap(BoxDecoration(body, title=header_text),
                             border_attr, 'focus')
        elif divider:
            # use a divider
            # we focus the divider to change colors when this
            # widget is focused
            styles = configuration.styles
            status_divider = styles.get('status_divider_char', '·')

            divider = AttrMap(Divider(status_divider),
                              border_attr,
                              'focus')
            widget = Pile([header, body, divider], focus_item=2)
        else:
            widget = Pile([header, body], focus_item=1)
        return widget

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key

    def _create_header(self, status):
        """
        Return the header text for the status associated with this widget.
        """
        if is_DM(status):
            return self._dm_header(status)

        reply = ''
        retweeted = ''
        retweet_count = ''
        retweeter = ''
        username = status.user
        relative_created_at = status.relative_created_at

        # reply
        if status.is_reply:
            reply = u' \u2709'

        # retweet
        if status.is_retweet:
            retweeted = u" \u267b "
            # `username` is the author of the original tweet
            username = status.author
            # `retweeter` is the user who made the RT
            retweeter = status.user
            retweet_count = str(status.retweet_count)

        # create header
        styles = configuration.styles
        header_template = ' ' + styles.get('header_template') + ' '
        header = unicode(header_template).format(
            username=username,
            retweeted=retweeted,
            retweeter=retweeter,
            time=relative_created_at,
            reply=reply,
            retweet_count=retweet_count,
        )

        return encode(header)

    def _dm_header(self, dm):
        dm_template = ''.join([' ', configuration.styles['dm_template'], ' '])
        relative_created_at = dm.relative_created_at
        header = unicode(dm_template).format(
            sender_screen_name=dm.sender_screen_name,
            recipient_screen_name=dm.recipient_screen_name,
            time=relative_created_at,
        )

        return encode(header)


class BoxDecoration(WidgetDecoration, WidgetWrap):
    """Draw a box around `original_widget`."""

    def __init__(self, original_widget, title="",
                 tlcorner=u'┌', tline=u'─', lline=u'│',
                 trcorner=u'┐', blcorner=u'└', rline=u'│',
                 bline=u'─', brcorner=u'┘'):
        """
        Use 'title' to set an initial title text with will be centered
        on top of the box.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner
        """

        tline, bline = Divider(tline), Divider(bline)
        lline, rline = SolidFill(lline), SolidFill(rline)
        tlcorner, trcorner = Text(tlcorner), Text(trcorner)
        blcorner, brcorner = Text(blcorner), Text(brcorner)

        title_widget = ('fixed', len(title), AttrMap(Text(title), 'header'))
        top = Columns([
            ('fixed', 1, tlcorner),
            title_widget,
            tline,
            ('fixed', 1, trcorner)
        ])

        middle = Columns([('fixed', 1, lline),
                          original_widget,
                          ('fixed', 1, rline)],
                         box_columns=[0, 2],
                         focus_column=1)

        bottom = Columns([('fixed', 1, blcorner),
                          bline,
                          ('fixed', 1, brcorner)])

        pile = Pile([('flow', top),
                     middle,
                     ('flow', bottom)],
                     focus_item=1)

        WidgetDecoration.__init__(self, original_widget)
        WidgetWrap.__init__(self, pile)


# - User ----------------------------------------------------------------------


class UserInfo(WidgetWrap):
    """
    A widget for displaying a Twitter user info.
    """

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, user):
        """
        """
        whitespace = Divider(' ')
        widgets = []

        # name
        name = Text('%s' % user.name)
        widgets.extend([name, whitespace])

        # bio
        if user.description:
            description = Text(parse_attributes(user.description))
            widgets.extend([description, whitespace])

        # URL
        if user.url:
            url_text_with_attr = ('url', user.url)
            url = Text(url_text_with_attr)

            widgets.extend([url, whitespace])

        # statistics: following, followers and favorites
        following = Text(_('following:\n%s' % user.friends_count))
        followers = Text(_('followers:\n%s' % user.followers_count))
        favorites = Text(_('favorites:\n%s' % user.favorites_count))
        stats = Columns([following, followers, favorites])

        widgets.extend([stats, whitespace])

        # last status
        if user.status:
            status = StatusWidget(user.status)
            widgets.append(status)

        pile = Pile(widgets)

        WidgetWrap.__init__(self, LineBox(title='@%s' % user.screen_name,
                                          original_widget=pile))
