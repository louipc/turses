###############################################################################
#                               coding=utf-8                                  #
#                      Copyright (c) 2012 Alejandro Gómez.                    #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from urwid import Frame, connect_signal, disconnect_signal
from widget import WelcomeBuffer, TabsWidget, TimelineBuffer, Footer, HelpBuffer
from widget import TextEditor, TweetEditor, DmEditor


class UserInterface(object):
    """Base API that a UI for turses has to implement."""

    # -- Modes ----------------------------------------------------------------

    def timeline_mode(self, timelines):
        """Activates the Timeline mode."""
        raise NotImplementedError

    def is_in_timeline_mode(self):
        raise NotImplementedError

    def info_mode(self):
        """Shows program info."""
        raise NotImplementedError

    def is_in_info_mode(self):
        raise NotImplementedError

    def help_mode(self, configuration):
        """Activates help mode."""
        raise NotImplementedError

    def is_in_help_mode(self):
        raise NotImplementedError

    # -- Header ---------------------------------------------------------------

    def clear_header(self):
        raise NotImplementedError

    def update_header(self, timelines):
        raise NotImplementedError

    # -- Footer ---------------------------------------------------------------
        
    def status_message(self, text):
        """Sets `text` as a status message on the footer."""
        raise NotImplementedError

    def status_error_message(self, message):
        raise NotImplementedError

    def status_info_message(self, message):
        raise NotImplementedError

    def clear_status(self):
        """Clears the status bar."""
        raise NotImplementedError

    # -- Timeline mode --------------------------------------------------------

    def draw_timeline(self, timeline):
        raise NotImplementedError

    def set_tab_names(self, names):
        raise NotImplementedError

    def activate_tab(self, index):
        raise NotImplementedError

    def focused_status(self):
        raise NotImplementedError

    # -- Editors --------------------------------------------------------------

    def show_text_editor(self, 
                         prompt='', 
                         content='', 
                         done_signal_handler=None):
        raise NotImplementedError

    def show_tweet_editor(self, 
                          prompt='', 
                          content='', 
                          done_signal_handler=None):
        raise NotImplementedError

    def show_dm_editor(self, 
                       prompt='', 
                       content='',
                       done_signal_handler=None):
        raise NotImplementedError

    def remove_editor(self, done_signal_handler):
        raise NotImplementedError

    def disconnect_editor_done_signal(self, done_signal_handler):
        raise NotImplementedError


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
        return self.footer.__class__ == HelpBuffer

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
