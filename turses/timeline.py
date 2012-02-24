###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


# TODO: 
#  - comparation for not repeating them in timeline
#  - helper functions
class Status():
    pass


class TimelineException(Exception):
    pass


class Timeline(object):
    """List of Twitter statuses ordered reversely by date."""

    def __init__(self, statuses=[]):
        self.statuses = sorted(statuses,
                               key=lambda status: status.created_at,
                               reverse=True)

    def add_status(self, new_status):
        """
        Adds the given status to the status list of the Timeline if it's
        not already in it.
        """
        # TODO insert ordered
        self.statuses.insert(0, new_status)
        self.statuses = sorted(self.statuses,
                              key=lambda status: status.created_at,
                              reverse=True)

    def add_statuses(self, new_statuses):
        """
        Adds the given new statuses to the status list of the Timeline
        if they are not already in it.
        """
        for status in new_statuses:
            self.add_status(status)

    def __len__(self):
        return len(self.statuses)

    def __iter__(self):
        return self.statuses.__iter__()

    def __getitem__(self, i):
        return self.statuses[i]
