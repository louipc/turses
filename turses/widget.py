###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from time import altzone, gmtime, strftime

import urwid

from util import is_retweet, encode


class TextEditor(urwid.WidgetWrap):
    """Editor for creating arbitrary text."""

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def __init__(self, prompt='', content=''):
        if content:
            content += ' '
        self.editor = Editor(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)

        urwid.connect_signal(self.editor, 'done', self.emit_done_signal)

        self.__super.__init__(self.editor)

    def emit_done_signal(self, content):
        urwid.emit_signal(self, 'done', content)


class TweetEditor(urwid.WidgetWrap):
    """Editor for creating tweets."""

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']

    def __init__(self, prompt='', content=''):
        if content:
            content += ' '
        self.editor = Editor(u'%s (twice enter key to validate or esc) \n>> ' % prompt, content)
        self.counter = urwid.Text('0')
        w = urwid.Columns([ ('fixed', 4, self.counter), self.editor])

        urwid.connect_signal(self.editor, 'done', self.emit_done_signal)
        urwid.connect_signal(self.editor, 'change', self.update_count)

        self.__super.__init__(w)

    def emit_done_signal(self, content):
        urwid.emit_signal(self, 'done', content)

    def update_count(self, edit, new_edit_text):
        self.counter.set_text(str(len(new_edit_text)))


class Editor(urwid.Edit):
    """
    Basic editor widget.
    
    The editing action is confirmed pressing <CR> twice in a row and cancelled
    pressing <Esc>.
    """

    __metaclass__ = urwid.signals.MetaSignals
    signals = ['done']
    last_key = ''

    def keypress(self, size, key):
        if key == 'enter' and self.last_key == 'enter':
            urwid.emit_signal(self, 'done', self.get_edit_text())
            return
        elif key == 'esc':
            urwid.emit_signal(self, 'done', None)
            return

        self.last_key = key
        urwid.Edit.keypress(self, size, key)


class TabsWidget(urwid.WidgetWrap):
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
        text = self._create_text()
        urwid.WidgetWrap.__init__(self, urwid.Text(text))

    def _is_valid_index(self, index):
        return index >= 0 and index < len(self.tabs)

    def _create_text(self):
        """Creates the text that is rendered as the tab list."""
        text = []
        for i, tab in enumerate(self.tabs):
            tab = tab + ' '
            if i == self.active_index:
                text.append(('active_tab', tab))
            else:
                text.append(('inactive_tab', tab))
        return text

    def _update_text(self):
        text = self._create_text()
        self._w.set_text(text)

    def append_tab(self, tab):
        self.tabs.append(tab)
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


class BufferFooter(urwid.WidgetWrap):
    def __init__(self, text=''):
        urwid.WidgetWrap.__init__(self, urwid.Text(text))


class TimelineBuffer(urwid.WidgetWrap):
    """A widget that displays a `Timeline` object."""

    def __init__(self, timeline=[]):
        urwid.WidgetWrap.__init__(self, TimelineWidget(timeline))

    def clear(self):
        """Clears the buffer."""
        return self.render_timeline([])

    def render_timeline(self, timeline):
        """Renders the given statuses."""
        self._w = TimelineWidget(timeline)


class TimelineWidget(urwid.ListBox):
    """
    A `urwid.ListBox` containing a list of Twitter statuses, each of which is
    rendered as a `StatusWidget`.
    """

    def __init__(self, timeline):
        status_widgets = [StatusWidget(status) for status in timeline]
        urwid.ListBox.__init__(self, urwid.SimpleListWalker(status_widgets))


class StatusWidget(urwid.WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__ (self, status):
        self.status = status
        self.id = status.id
        status_content = urwid.Padding(
            urwid.AttrWrap(urwid.Text(status.text), 'body'), 
            left=1, 
            right=1)
        header = self.create_header(status)
        widget = urwid.AttrWrap(BoxDecoration(status_content, title=header), 
                                'line', 
                                'focus')
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
            
        # TODO take template from configuration
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


class BoxDecoration(urwid.WidgetDecoration, urwid.WidgetWrap):
    """Draw a box around `original_widget`."""

    def __init__(self, original_widget, title=''):
        self.color = 'header'
        if int(urwid.__version__[0]) == 1:
            urwid.utf8decode = lambda string: string

        def use_attr(a, t):
            if a:
                t = urwid.AttrWrap(t, a)
            return t

        # top line
        tline = None
        tline_attr = urwid.Columns([('fixed', 2, 
                                        urwid.Divider(urwid.utf8decode("─"))),
                                    ('fixed', len(title), 
                                        urwid.AttrWrap(urwid.Text(title), self.color)),
                                    urwid.Divider(urwid.utf8decode("─")),])
        tline = use_attr(tline, tline_attr)
        # bottom line
        bline = None
        bline = use_attr(bline, urwid.Divider(urwid.utf8decode("─")))
        # left line
        lline = None
        lline = use_attr(lline, urwid.SolidFill(urwid.utf8decode("│")))
        # right line
        rline = None
        rline = use_attr(rline, urwid.SolidFill(urwid.utf8decode("│")))
        # top left corner
        tlcorner = None
        tlcorner = use_attr(tlcorner, urwid.Text(urwid.utf8decode("┌")))
        # top right corner
        trcorner = None
        trcorner = use_attr(trcorner, urwid.Text(urwid.utf8decode("┐")))
        # bottom left corner
        blcorner = None
        blcorner = use_attr(blcorner, urwid.Text(urwid.utf8decode("└")))
        # bottom right corner
        brcorner = None
        brcorner = use_attr(brcorner, urwid.Text(urwid.utf8decode("┘")))

        # top
        top = urwid.Columns([('fixed', 1, tlcorner),
                             tline, 
                             ('fixed', 1, trcorner),])
        # middle
        middle = urwid.Columns([('fixed', 1, lline),
                                original_widget, 
                                ('fixed', 1, rline)], 
                               box_columns = [0,2], 
                               focus_column = 1)
        # bottom
        bottom = urwid.Columns([('fixed', 1, blcorner),
                                bline, 
                                ('fixed', 1, brcorner)])

        # widget decoration
        pile = urwid.Pile([('flow',top),
                           middle,
                           ('flow',bottom)], 
                          focus_item = 1)

        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, pile)
