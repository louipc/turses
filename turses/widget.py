###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid


class BufferHeader(urwid.WidgetWrap):
    """Displays the names of the buffers, highlighting the active buffer."""

    def __init__(self, buffer_names):
        self.buffer_names = buffer_names
        self.active_index = 0
        text = self._create_text()
        urwid.WidgetWrap.__init__(self, urwid.Text(text))

    def _create_text(self):
        """Creates the text that is rendered as the header."""
        text = []
        for i, name in enumerate(self.buffer_names):
            buffer_tab = name + ' '
            if i == self.active_index:
                text.append(('active_tab', buffer_tab))
            else:
                text.append(('inactive_tab', buffer_tab))
        return text

    def _update_text(self):
        text = self._create_text()
        self._w.set_text(text)

    def append_buffer_name(self, buffer_name):
        self.buffer_names.append(buffer_name)
        self._update_text()

    def remove_current_buffer_name(self):
        del self.buffer_names[self.active_index]
        self._update_text()

    def set_active_buffer(self, pos):
        self.active_index = pos
        self._update_text()


#TODO
class BufferFooter(urwid.WidgetWrap):
    pass


class BufferListException(Exception):
    pass


class BufferList(urwid.WidgetWrap):
    """
    A tabbed list of buffers.
    
    It is instantiated giving it a list of buffers that cannot be
    empty.
    """

    def __init__(self, buffers=[]):
        if buffers:
            self.buffers = buffers
            self.active_buffer = self.buffers[0]
            self.header = BufferHeader([buffer.name for buffer in self.buffers])
            urwid.WidgetWrap.__init__(self, 
                                      urwid.Frame(self.buffers[0],
                                                  header=self.header),)
        else:
            raise BufferListException('`BufferList` must be instantiated at least' \
                                        'with one buffer instance.')

    def _is_valid_index(self, index):
        return index >= 0 and index < len(self.buffers)

    def _active_buffer_index(self):
        return self.buffers.index(self.active_buffer)
        
    def _has_previous_buffer(self):
        return self._active_buffer_index() > 0

    def _has_next_buffer(self):
        return self._active_buffer_index() < len(self.buffers) - 1

    def display_buffer(self, index):
        """
        Displays the buffer that is in `index`-th position if it is
        within the bounds.
        """
        if not self._is_valid_index(index):
            return
        self.active_buffer = self.buffers[index]
        self.header.set_active_buffer(index)
        self._w = urwid.Frame(self.active_buffer,
                              header=self.header,)

    def display_previous_buffer(self):
        """
        Displays the previous buffer and considers it as the active buffer.

        If the active buffer is the first, it does nothing.
        """
        if self._has_previous_buffer():
            new_index = self._active_buffer_index() - 1
            self.active_buffer = self.buffers[new_index]
            self.display_buffer(new_index)

    def display_next_buffer(self):
        """
        Displays the next buffer and considers it as the active buffer.

        If the active buffer is the last, it does nothing.
        """
        if self._has_next_buffer():
            new_index = self._active_buffer_index() + 1
            self.active_buffer = self.buffers[new_index]
            self.display_buffer(new_index)

    def append_buffer(self, buffer):
        """Appends a new buffer to the end of the list."""
        self.buffers.append(buffer)

    def update(self):
        """Updates every `TimelineBuffer` in this `BufferList`."""
        for buffer in self.buffers:
            buffer.update()

    def __iter__(self):
        return self.buffers.__iter__()
        

class TimelineBuffer(urwid.WidgetWrap):
    """A widget that displays its associated `Timeline` object."""

    def __init__(self, name, timeline=[]):
        self.name = name
        self.timeline = timeline
        urwid.WidgetWrap.__init__(self, TimelineWidget(timeline))

    def clear(self):
        """Clears its Timeline and the UI."""
        self.timeline.clear()
        self.update()

    def update(self):
        """
        Reads the statuses from its Timeline and updates the widget
        accordingly.
        """
        self._w = TimelineWidget(self.timeline)


class TimelineWidget(urwid.ListBox):
    """
    A `urwid.ListBox` containing a list of Twitter statuses, each of which is
    rendered as a `StatusWidget`.
    """

    def __init__(self, content):
        status_widgets = [StatusWidget(status) for status in content]
        urwid.ListBox.__init__(self, urwid.SimpleListWalker(status_widgets))


class StatusWidget(urwid.WidgetWrap):
    """Widget containing a Twitter status."""

    def __init__ (self, status):
        self.status = status
        self.id = status.id
        status_content = urwid.Padding(
            urwid.AttrWrap(urwid.Text(status.text), 'body'), left=1, right=1)
        # TODO!Header
        widget = urwid.AttrWrap(BoxDecoration(status_content, title=status.user.screen_name), 
                                              'line', 
                                              'focus')
        self.__super.__init__(widget)

    def selectable(self):
        return True

    def keypress(self, size, key):
        #TODO! modify widget attributes in response to certain actions
        return key


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
