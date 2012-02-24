###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from datetime import datetime

##
#  Helper functions
##

def datetime_from_status(status):
    """Converts a date on a Twitter status to a `datetime` object."""
    seconds = status.GetCreatedAtInSeconds()
    return datetime.utcfromtimestamp(seconds)

def is_more_recent(status, datetime):
    """Checks wether `status.created_at` is newer than `datetime`."""
    created_at = datetime_from_status(status)
    return created_at > datetime


##
#  Classes
##
    

class Timeline(object):
    """
    List of Twitter statuses ordered reversely by date. Optionally with
    a function that updates the current timeline and its arguments.
    """

    def __init__(self, 
                 statuses=[],
                 update_function=None,
                 update_function_args=None):
        self._key = lambda status: datetime_from_status(status)
        if statuses:
            self.statuses = sorted(statuses,
                                   key=self._key,
                                   reverse=True)
        else:
            self.statuses = statuses
        self.update_function = update_function
        self.update_function_args = update_function_args

    def add_status(self, new_status):
        """
        Adds the given status to the status list of the Timeline if it's
        not already in it.
        """
        if new_status not in self.statuses:
            self.statuses.append(new_status)
            self.statuses.sort(key=self._key, reverse=True)

    def add_statuses(self, new_statuses):
        """
        Adds the given new statuses to the status list of the Timeline
        if they are not already in it.
        """
        for status in new_statuses:
            self.add_status(status)

    def clear(self):
        """Clears the Timeline."""
        self.statuses = []

    def get_newer_than(self, datetime):
        """Returns the statuses that are more recent than `datetime`."""
        return filter(lambda status : is_more_recent(status, datetime),
                      self.statuses)

    def update(self):
        if self.update_function_args:
            new_statuses = self.update_function(self.update_function_args)
        else:
            new_statuses = self.update_function()
        self.add_statuses(new_statuses)

    def __len__(self):
        return len(self.statuses)

    def __iter__(self):
        return self.statuses.__iter__()

    def __getitem__(self, i):
        return self.statuses[i]
