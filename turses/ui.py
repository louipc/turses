# -*- coding: utf-8 -*-

"""
turses.ui
~~~~~~~~~

This module contains the UI widgets.
"""

from gettext import gettext as _

from urwid import (AttrMap, WidgetWrap, Padding, Divider, SolidFill,
                   WidgetDecoration, Filler,

                   # widgets
                   Text, Edit, Frame, Columns, Pile, ListBox, SimpleListWalker,
                   Overlay,

                   # signals
                   signals, emit_signal, connect_signal, disconnect_signal)

from turses import version
from turses.config import (MOTION_KEY_BINDINGS, BUFFERS_KEY_BINDINGS,
                           TWEETS_KEY_BINDINGS, TIMELINES_KEY_BINDINGS,
                           META_KEY_BINDINGS, TURSES_KEY_BINDINGS, )
from turses.models import is_DM, TWEET_MAXIMUM_CHARACTERS
from turses.utils import encode


# - Main UI -------------------------------------------------------------------


class CursesInterface(Frame):
    """
    Creates a curses interface for the program, providing functions to draw
    all the components of the UI.
    """

    def __init__(self,
                 configuration):
        header = TabsWidget()

        body = Banner(configuration)
        self._status_bar = configuration.styles.get('status_bar', False)
        if self._status_bar:
            footer = StatusBar('')
        else:
            footer = None

        Frame.__init__(self,
                       body,
                       header=header,
                       footer=footer)
        self._configuration = configuration
        self._editor = None

    # -- Modes ----------------------------------------------------------------

    def draw_timelines(self, timelines):
        self.body = TimelinesBuffer(timelines,
                                    configuration=self._configuration)
        self.set_body(self.body)

    def show_info(self):
        self.header.clear()
        self.body = Banner(self._configuration)
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

    def _can_write_status(self):
        if self._status_bar:
            if self.footer is None:
                self.footer = StatusBar('')
            return True
        return False

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
        self._editor = editor_cls(prompt=prompt,
                                  content=content,
                                  done_signal_handler=done_signal_handler,
                                  **kwargs)

        styles = self._configuration.styles
        horizontal_align = styles['editor_horizontal_align']
        vertical_align = styles['editor_vertical_align']

        self.body.show_widget_on_top(widget=self._editor,
                                     width=80,
                                     height=3,
                                     align=horizontal_align,
                                     valign=vertical_align)
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
        except:
            # `disconnect_signal` raises an exception if no signal was
            # connected from `self._editor`. We can safely ignore it.
            pass
        self._editor = None
        self.body.hide_top_widget()


# - Program info --------------------------------------------------------------


class Banner(WidgetWrap):
    """Displays information about the program."""

    def __init__(self, configuration):
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

        The subclasses must call the WidgetWrap constructor to create the
        actual widget.
        """
        caption = _(u'%s (twice enter key to validate or esc) \n>> ') % prompt
        if content:
            content += ' '
        self.content = content
        self.editor = Edit(caption=caption,
                           edit_text=content,
                           edit_pos=cursor_position)

        connect_signal(self, 'done', done_signal_handler)

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

        widgets = [self.editor]
        w = AttrMap(Columns(widgets), 'editor')

        WidgetWrap.__init__(self, w)


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

        widgets = [('fixed', 4, self.counter_widget), self.editor]
        w = AttrMap(Columns(widgets), 'editor')

        connect_signal(self.editor, 'change', self.update_counter)

        WidgetWrap.__init__(self, w)

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


# - Help ----------------------------------------------------------------------


class HelpBuffer(ScrollableListBoxWrapper):
    """
    A widget that displays all the keybindings of the given configuration.
    """

    col = [30, 7]

    def __init__(self, configuration):
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


# - Timelines -----------------------------------------------------------------


class TimelinesBuffer(WidgetWrap):
    """
    A widget that displays one or more `Timeline` objects.
    
    Another widget can be placed on top of it.
    """

    def __init__(self, timelines=None, **kwargs):
        timelines = [] if timelines is None else timelines

        widget = self._create_widget(timelines, **kwargs)

        WidgetWrap.__init__(self, widget)

    def _create_widget(self, timelines, **kwargs):
        timeline_widgets = [TimelineWidget(timeline, **kwargs) for timeline
                                                                in timelines]
        columns = Columns(timeline_widgets) 

        return self._create_overlay(columns)

    def _create_overlay(self, top_w):
        # NOTE:
        # This is an ugly hack for being able to show a widget on top when
        # needed. I create the Overlay with a dummy_widget on the bottom that
        # will never be visible (making the top widget big enough).
        dummy_widget = ListBox(SimpleListWalker([]))
        return Overlay(top_w=top_w,
                       bottom_w=dummy_widget,
                       align='center',
                       width=200,
                       valign='middle',
                       height=200)

    def render_timelines(self, timelines, **kwargs):
        """Render the given statuses."""
        self._w = self._create_widget(timelines, **kwargs)

    @property
    def columns(self):
        """
        The `Columns` widget.
        """
        top = self._w.top_w
        bottom = self._w.bottom_w
        return top if isinstance(top, Columns) else bottom

    @property
    def active_widget(self):
        """
        The active widget.
        """
        return self.columns.get_focus()

    def show_widget_on_top(self,
                           widget,
                           width,
                           height,
                           align='center',
                           valign='middle'):
        widget = Filler(widget)
        self._w.bottom_w, self._w.top_w = self._w.top_w, widget
        self._w.set_overlay_parameters(align=align,
                                       width=width,
                                       valign=valign,
                                       height=height,
                                       min_width=width,
                                       min_height=height)

    def hide_top_widget(self):
        self._w = self._create_overlay(self.columns)

    def scroll_up(self):
        self.active_widget.focus_previous()

    def scroll_down(self):
        self.active_widget.focus_next()

    def scroll_top(self):
        self.active_widget.focus_first()

    def scroll_bottom(self):
        self.active_widget.focus_last()

    def clear(self):
        """Clears the buffer."""
        # FIXME
        pass

    def set_focus(self, index):
        self.active_widget.set_focus(index)

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
    A `ListBox` containing a list of Twitter statuses, each of which is
    rendered as a `StatusWidget`.
    """

    def __init__(self, timeline=None, configuration=None):
        statuses = timeline if timeline else []
        status_widgets = [StatusWidget(status, configuration) for status
                                                              in statuses]
        ScrollableListBox.__init__(self, status_widgets)


class StatusWidget(WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__(self, status, configuration):
        self.status = status
        self.configuration = configuration

        header_text = self._create_header(status)
        text = status.map_attributes(hashtag='hashtag',
                                     attag='attag',
                                     url='url')

        is_favorite = not is_DM(status) and status.is_favorite
        widget = self._build_widget(header_text, text, is_favorite)

        self.__super.__init__(widget)

    def _build_widget(self, header_text, text, favorite=False):
        """Return the wrapped widget."""
        box_around_status = self.configuration.styles.get('box_around_status',
                                                          True)
        divider = self.configuration.styles.get('status_divider',
                                                False)

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
            styles = self.configuration.styles
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

        # tweet or retweet
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
        styles = self.configuration.styles
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
        dm_template = ' ' + self.configuration.styles['dm_template'] + ' '
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
