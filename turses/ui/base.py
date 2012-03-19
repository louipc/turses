###############################################################################
#                               coding=utf-8                                  #
#            Copyright (c) 2012 turses contributors. See AUTHORS.             #
#         Licensed under the GPL License. See LICENSE for full details.       #
###############################################################################


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

    def set_focus(self, index):
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
