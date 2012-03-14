###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


from time import altzone, gmtime, strftime
from gettext import gettext as _

from urwid import AttrWrap, WidgetWrap, Padding, WidgetDecoration
from urwid import Text, Edit, Frame, Columns, Pile, Divider, SolidFill
from urwid import ListBox, SimpleListWalker
from urwid import signals, emit_signal, connect_signal, disconnect_signal
from urwid import __version__ as urwid_version

from ..util import is_retweet, encode, html_unescape
from ..constant import banner
from .base import UserInterface


TWEET_MAX_CHARS = 140

class CursesInterface(Frame, UserInterface):
    """
    Creates a curses interface for the program, providing functions to draw 
    all the components of the UI.
    """

    def __init__(self):
        Frame.__init__(self,
                       WelcomeBuffer(),
                       header=TabsWidget(),
                       footer=Footer(''))

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self, timelines):
        """Activates the Timeline mode."""
        if timelines.has_timelines():
            self.draw_timelines(timelines)

    def is_in_timeline_mode(self):
        return self.body.__class__ == TimelineBuffer

    def info_mode(self):
        """Shows program info."""
        self.header.clear()
        self.body = WelcomeBuffer()
        self.set_body(self.body)

    def is_in_info_mode(self):
        return self.body.__class__ == WelcomeBuffer

    def help_mode(self, configuration):
        """Activates help mode."""
        self.clear_header()
        self.status_info_message('Type <Esc> to leave the help page.')
        self.body = HelpBuffer(configuration)
        self.set_body(self.body)

    def is_in_help_mode(self):
        return self.body.__class__ == HelpBuffer

    # -- Header ---------------------------------------------------------------

    def clear_header(self):
        self.header.clear()

    def update_header(self, timelines):
        self.header.set_tabs(timelines.get_timeline_names())
        self.header.set_active_tab(timelines.active_index)

    # -- Footer ---------------------------------------------------------------
        
    def status_message(self, text):
        """Sets `text` as a status message on the footer."""
        if self.footer.__class__ is not Footer:
            self.footer = Footer()
        self.footer.message(text)
        self.set_footer(self.footer)

    def status_error_message(self, message):
        self.status_message("[error] " + message)

    def status_info_message(self, message):
        self.status_message("[info] " + message)

    def clear_status(self):
        """Clears the status bar."""
        self.footer = Footer()
        self.set_footer(self.footer)

    # -- Timeline mode --------------------------------------------------------

    def draw_timeline(self, timeline):
        self.body = TimelineBuffer()
        self.body.render_timeline(timeline)
        self.set_body(self.body)

    def set_tab_names(self, names):
        self.header.set_tabs(names)
        self.set_header(self.header)

    def activate_tab(self, index):
        self.header.set_active_tab(index)
        self.set_header(self.header)

    def focused_status(self):
        if self.is_in_timeline_mode():
            return self.body.get_focused_status()

    # -- Editors --------------------------------------------------------------

    def _show_editor(self,
                     editor_cls,
                     prompt,
                     content,
                     done_signal_handler):
        self.footer = editor_cls(prompt, content)
        self.set_footer(self.footer)
        self.set_focus('footer')
        connect_signal(self.footer, 'done', done_signal_handler)

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
                       done_signal_handler=None):
        self._show_editor(DmEditor,
                          prompt,
                          content,
                          done_signal_handler,)

    def remove_editor(self, done_signal_handler):
        disconnect_signal(self, self.footer, 'done', done_signal_handler)
        self.clear_status()

    def disconnect_editor_done_signal(self, done_signal_handler):
        disconnect_signal(self, self.footer, 'done', done_signal_handler)


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

    def __init__(self, prompt='', content=''):
        if content:
            content += ' '
        self.editor = Editor(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)

        connect_signal(self.editor, 'done', self.emit_done_signal)

        self.__super.__init__(self.editor)

    def emit_done_signal(self, content):
        emit_signal(self, 'done', content)


class TweetEditor(WidgetWrap):
    """Editor for creating tweets."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, prompt='', content=''):
        if content:
            content += ' '
        self.editor = Editor(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)
        self.counter = len(content)
        self.counter_widget = Text(str(self.counter))
        w = Columns([('fixed', 4, self.counter_widget), self.editor])

        connect_signal(self.editor, 'done', self.emit_done_signal)
        connect_signal(self.editor, 'change', self.update_counter)

        self.__super.__init__(w)
    
    def emit_done_signal(self, content):
        emit_signal(self, 'done', content)

    def update_counter(self, edit, new_edit_text):
        self.counter = len(new_edit_text)
        self.counter_widget.set_text(str(self.counter))

    def keypress(self, size, key):
        if self.counter > TWEET_MAX_CHARS and key == 'enter' and self.editor.last_key == 'enter':
                return
        Editor.keypress(self.editor, size, key)


class DmEditor(TweetEditor):
    """Editor for creating DMs."""

    __metaclass__ = signals.MetaSignals
    signals = ['done']

    def __init__(self, recipient, prompt='', content=''):
        self.recipient = recipient
        TweetEditor.__init__(self, prompt, content)
    
    def emit_done_signal(self, content):
        emit_signal(self, 'done', self.recipient, content)


class Editor(Edit):
    """
    Basic editor widget.
    
    The editing action is confirmed pressing <CR> twice in a row and cancelled
    pressing <Esc>.
    """

    __metaclass__ = signals.MetaSignals
    signals = ['done']
    last_key = ''

    def keypress(self, size, key):
        if key == 'enter' and self.last_key == 'enter':
            emit_signal(self, 'done', self.get_edit_text())
            return
        elif key == 'esc':
            emit_signal(self, 'done', None)
            return

        self.last_key = key
        Edit.keypress(self, size, key)


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
        else:
            self.active_index = -1
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
                text.append(('active_tab', u'│' + tab + u'│'))
            else:
                text.append(('inactive_tab', u' ' + tab + u' '))
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

    def set_tabs(self, tabs):
        self.tabs = tabs
        self._update_text()

    def clear(self):
        self._w.set_text('')


class Footer(WidgetWrap):
    """Displays a text."""
    def __init__(self, text=''):
        WidgetWrap.__init__(self, Text(text))

    def message(self, text):
        """Write `text` on the footer.""" 
        self._w.set_text(text)

    def clear(self):
        """Clear the text."""
        self._w.set_text('')


class ScrollableListBoxWrapper(WidgetWrap):
    """
    A `WidgetWrap` subclass intented to wrap `ScrollableListBox`
    elements, provides an interface for the scrolling capabilities.
    """
    def __init__(self, contents):
        WidgetWrap.__init__(self, contents)

    def scroll_up(self):
        self._w.focus_previous()

    def scroll_down(self):
        self._w.focus_next()

    def scroll_top(self):
        self._w.focus_first()

    def scroll_bottom(self):
        self._w.focus_last()


class ScrollableListBox(ListBox):
    """
    A `ListBox` subclass with additional methods for scrolling the
    focus up by one element, down by one element, to the bottom and to 
    the top.
    """
    def __init__(self, contents):
        ListBox.__init__(self, SimpleListWalker(contents))

    def focus_previous(self):
        """Sets the focus in the previous element (if any) of the listbox."""
        focus_status, pos = self.get_focus()
        if pos:
            self.set_focus(pos - 1)

    def focus_next(self):
        """Sets the focus in the next element (if any) of the listbox."""
        focus_status, pos = self.get_focus()
        if pos is not None and pos < len(self.body):
            self.set_focus(pos + 1)

    def focus_first(self):
        """Sets the focus in the first element (if any) of the listbox."""
        if len(self.body):
            self.set_focus(0)

    def focus_last(self):
        """Sets the focus in the last element (if any) of the listbox."""
        last = len(self.body) - 1
        if last:
            self.set_focus(last)


class ShiftScrollableListBox(ScrollableListBox):
    """
    A `ScrollableListBox` subclass that, instead of steping up and down 
    by one element, it changes focus to the first non-visible elements
    on top or bottom.
    """
    def focus_previous(self):
        """Sets the focus in the first non-visible widget of the top of
        the list (if any)."""
        # TODO
        pass

    def focus_next(self):
        """Sets the focus in the first non-visible widget of the botto of
        the list (if any)."""
        # TODO
        pass


class HelpBuffer(ScrollableListBoxWrapper):
    """
    A widget that displays all the keybindings of the given configuration.
    """

    col = [30, 7]

    def __init__ (self, configuration):
        self.configuration = configuration
        self.items = []
        w = AttrWrap(self.create_help_buffer(), 'body')
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
        self.insert_help_item('thread', _('Open selected thread'))
        self.insert_help_item('user_info', _('Show user information '))
        self.insert_help_item('help', _('Show help buffer'))

        # Others
        self.insert_division(_('Others'))
        self.insert_help_item('quit', _('Leave turses'))
        self.insert_help_item('openurl', _('Open URL in browser'))
        self.insert_help_item('open_image', _('Open image'))
        self.insert_help_item('redraw', _('Redraw the screen'))

        return ShiftScrollableListBox(self.items)

    def insert_division(self, title):
        self.items.append(Divider(' '))
        self.items.append(Padding(AttrWrap(Text(title), 'focus'), left=4))
        self.items.append(Divider(' '))

    def insert_header(self):
        self.items.append( Columns([
            ('fixed', self.col[0], Text('  Name')),
            ('fixed', self.col[1], Text('Key')),
            Text('Description')
        ]))

    def insert_help_item(self, key, description):
        self.items.append( Columns([
            ('fixed', self.col[0], Text('  ' + key)),
            ('fixed', self.col[1], Text(self.configuration.keys[key])),
            Text(description)
        ]))


class TimelineBuffer(ScrollableListBoxWrapper):
    """A widget that displays a `Timeline` object."""

    def __init__(self, timeline=None):
        WidgetWrap.__init__(self, TimelineWidget(timeline))

    def clear(self):
        """Clears the buffer."""
        return self.render_timeline([])

    def render_timeline(self, timeline):
        """Renders the given statuses."""
        self._w = TimelineWidget(timeline)

    def get_focused_status(self):
        widget = self._w.get_focused_widget()
        if widget:
            return widget.status


class TimelineWidget(ScrollableListBox):
    """
    A `ListBox` containing a list of Twitter statuses, each of which is
    rendered as a `StatusWidget`.
    """

    def __init__(self, timeline=None):
        statuses = timeline if timeline else []
        status_widgets = [StatusWidget(status) for status in statuses]
        ScrollableListBox.__init__(self, status_widgets)

    def get_focused_widget(self):
        """Returns the currently focused `StatusWidget` (if any)."""
        _, pos = self.get_focus()
        if pos is not None:
            widget = self.body[pos]
            return widget


class StatusWidget(WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__ (self, status):
        self.status = status
        self.id = status.id
        unescaped_text = html_unescape(status.text)
        status_content = Padding(
            AttrWrap(Text(unescaped_text), 'body'), 
            left=1, 
            right=1)
        header = self.create_header(status)
        box = BoxDecoration(status_content, title=header)
        if self.is_favorite(status):
            widget = AttrWrap(box, 'favorited', 'focus')
        else:
            widget = AttrWrap(box, 'line', 'focus')
        self.__super.__init__(widget)

    def selectable(self):
        return True

    def keypress(self, size, key):
        #TODO! modify widget attributes in response to certain actions
        return key

    def create_header(self, status):
        """Returns the header text for the status associated with this widget."""
        retweeted = ''
        reply = ''
        retweet_count = ''
        retweeter = ''
        source = self.get_source(status)
        username = self.get_username(status)
        time = self.get_time(status)

        if self.is_reply(status):
            reply = u' \u2709'
        if is_retweet(status):
            retweeted = u" \u267b "
            retweeter = username
            username = self.origin_of_retweet(status)

        if self.get_retweet_count(status):
            retweet_count = str(self.get_retweet_count(status))
            
        # TODO 
        #  - take template from configuration
        #  - {favorite} template variable
        header_template = ' {username}{retweeted}{retweeter} - {time}{reply} {retweet_count} '
        header = unicode(header_template).format(
            time = time,
            username= username,
            reply = reply,
            retweeted = retweeted,
            source = source,
            retweet_count = retweet_count,
            retweeter = retweeter
            )

        return encode(header)

    def get_source(self, status):
        source = ''
        if hasattr(status, 'source'):
            source = status.source
        return source

    def get_username(self, status):
        if hasattr(status, 'user'):
            nick = status.user.screen_name
        else:
            # Used for direct messages
            nick = status.sender_screen_name
        return nick

    def get_time(self, status):
        """
        Convert the time format given by the API to something more
        readable.

        Args:
          date: full iso time format.

        Returns string: human readable time.
        """
        if hasattr(status, 'GetRelativeCreatedAt'):
            return status.GetRelativeCreatedAt()

        hour = gmtime(status.GetCreatedAtInSeconds() - altzone)
        result = strftime('%H:%M', hour)
        if strftime('%d %b', hour) != strftime("%d %b", gmtime()):
            result += strftime(' - %d %b', hour)

        return result

    def is_reply(self, status):
        if hasattr(status, 'in_reply_to_screen_name'):
            reply = status.in_reply_to_screen_name
            if reply:
                return True
        return False

    def origin_of_retweet(self, status):
        """
        Returns the original author of the tweet being retweeted.
        """
        origin = status.text
        origin = origin[4:]
        origin = origin.split(':')[0]
        origin = str(origin)
        return origin

    def get_retweet_count(self, status):
        if hasattr(status, 'retweet_count'):
            return status.retweet_count

    def is_favorite(self, status):
        if hasattr(status, 'favorited'):
            return status.favorited


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


class UserBuffer(object):
    """
    A buffer that shows information for a certain user and its associated
    timelines.
    """
    # TODO
    pass


class UserWidget(object):
    """
    A widget with a user's information.
    """
    # TODO
    pass
