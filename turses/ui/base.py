# -*- coding: utf-8 -*-

"""
turses.ui.base
~~~~~~~~~~~~~~

This module contains the interfaces that different UI widgets must implement.
"""


class UserInterface(object):
    """Base API that a UI for turses has to implement."""

    # -- Modes ----------------------------------------------------------------

    def draw_timelines(self, timelines):
        """Draw the given `timelines`."""
        raise NotImplementedError

    def show_program_info(self):
        """Show program info."""
        raise NotImplementedError

    def show_help(self, configuration):
        """Show help based on `configuration`."""
        raise NotImplementedError

    # -- Header ---------------------------------------------------------------

    def clear_header(self):
        raise NotImplementedError

    def update_header(self, timelines):
        raise NotImplementedError

    # -- Footer ---------------------------------------------------------------
        
    def status_message(self, text):
        """Set `text` as a status message on the footer."""
        raise NotImplementedError

    def status_error_message(self, message):
        raise NotImplementedError

    def status_info_message(self, message):
        raise NotImplementedError

    def clear_status(self):
        """Clear the status bar."""
        raise NotImplementedError

    # -- Timeline mode --------------------------------------------------------

    def set_focus(self, index):
        raise NotImplementedError

    def set_tab_names(self, names):
        raise NotImplementedError

    def activate_tab(self, index):
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


class Tabs(object):
    """
    A widget that renders tabs with the given strings as titles.

    One of them is highlighted as the active tab.
    """
    def append_tab(self, tab):
        raise NotImplementedError

    def delete_current_tab(self):
        raise NotImplementedError

    def set_active_tab(self, pos):
        raise NotImplementedError

    def set_tabs(self, tabs):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError


class Status(object):
    """Displays a text with context-aware attributes."""

    def message(self, text):
        """Show `text` as the message.""" 
        raise NotImplementedError

    def error_message(self, text):
        raise NotImplementedError

    def info_message(self, text):
        raise NotImplementedError

    def clear(self):
        """Clear the text."""
        raise NotImplementedError


class Scrollable(object):
    """A set of methods that the scrollable widgets must implement."""

    def scroll_up(self):
        """Sets the focus in the previous element (if any) of the widget."""
        raise NotImplementedError

    def scroll_down(self):
        """Sets the focus in the next element (if any) of the widget."""
        raise NotImplementedError

    def scroll_top(self):
        """Sets the focus in the first element (if any) of the widget."""
        raise NotImplementedError

    def scroll_bottom(self):
        """Sets the focus in the last element (if any) of the widget."""
        raise NotImplementedError
