###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

class BufferList(urwid.Frame):
    """
    Keeps a list of buffers and provides functions to switch their visibility,
    rendering one at a time.
    """
    def __init__(self, buffers=[], header=None, footer=None):
        self.buffers = buffers
        self.header = header
        self.footer = footer
        if self.buffers:
            self.set_buffer(self.buffers[0])
        
    def set_buffer(self, buffer):
        self.current_buffer = buffer
        urwid.Frame.__init__(self, self.current_buffer, header=self.header, footer=self.footer)

    def _has_previous(self, buffer):
        current_buffer_index = self.buffers.index(buffer)
        return current_buffer_index > 0

    def _has_next(self, buffer):
        current_buffer_index = self.buffers.index(buffer)
        return current_buffer_index < len(self.buffers) - 1

    def prev_buffer(self):
        if self._has_previous(self.current_buffer):
            new_index = self.buffers.index(self.current_buffer) - 1
            new_buffer = self.buffers[new_index]
            self.set_buffer(new_buffer)

    def next_buffer(self):
        if self._has_next(self.current_buffer):
            new_index = self.buffers.index(self.current_buffer) + 1
            new_buffer = self.buffers[new_index]
            self.set_buffer(new_buffer)

    def add_buffer(self, buffer):
        self.buffers.append(buffer)

    def remove_buffer(self, buffer):
        if len(self.buffers) == 1 and buffer in self.buffers:
            raise urwid.ExitMainLoop()
        try:
            if self._has_previous(buffer):
                self.prev_buffer()
            else:
                self.next_buffer()
            self.buffers.remove(buffer)
        except ValueError:
            pass


class TimelineBuffer(urwid.WidgetWrap):
    def __init__(self, timeline):
        self.timeline = timeline
        urwid.WidgetWrap.__init__(self, TimelineWidget(timeline))
        self.timeline.set_update_callback(self._w.update)

    #TODO! make this happen periodically in a separate thread
    def update(self):
        self.timeline.update_timeline()


class TimelineWidget(urwid.ListBox):
    def __init__(self, content):
        widgets = [self._status_to_widget(status) for status in content]
        urwid.ListBox.__init__(self, StatusWalker(widgets))

    def _status_to_widget(self, status):
        return StatusWidget(status)

    def update(self, new_content):
        for status in new_content:
            widget = self._status_to_widget(status)
            self.body.insert(0, widget)


class StatusWalker(urwid.SimpleListWalker):
    def __init__(self, content):
        urwid.SimpleListWalker.__init__(self, content)


class StatusWidget(urwid.WidgetWrap):
    """Widget containing a Twitter status."""
    def __init__ (self, status):
        #TODO!id
        self.status = status
        self.id = status.id
        status_content = urwid.Padding(
            urwid.AttrWrap(urwid.Text(status.get_text()), 'body'), left=1, right=1)
        # TODO!Header
        widget = urwid.AttrWrap(BoxDecoration(status_content, title=status.get_username()), 
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
