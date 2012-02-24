###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


class TimelineManager(object):
    """
    Keeps information about a `Timeline` object and the API function
    call that updates the timeline.
    """
    def __init__(self, 
                 timeline, 
                 api_update_function, 
                 api_update_function_args=None):
        """ TODO """
        self.timeline = timeline
        self.update_function = api_update_function
        self.update_function_args = api_update_function_args

    def update(self):
        if self.update_function_args:
            new_statuses = self.update_function(self.update_function_args)
        else:
            new_statuses = self.update_function()
        self.timeline.add_statuses(new_statuses)
