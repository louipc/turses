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


class NamedTimelineList(object):
    """
    A list of (name, timeline) tuples. Only one is the 'active'
    timeline.
    """

    def __init__(self):
        self.timelines = []
        self.active_index = -1

    def _is_valid_index(self, index):
        return index >= 0 and index < len(self.timelines)

    def has_timelines(self):
        return self.active_index != -1 and self.timelines

    def get_active_timeline_name(self):
        if self.has_timelines():
            name, _ = self.timelines[self.active_index]
            return name
        else:
            raise Exception("There are no timelines in the list")

    def get_active_timeline(self):
        if self.has_timelines():
            _, timeline = self.timelines[self.active_index]
            return timeline
        else:
            raise Exception("There are no timelines in the list")

    def append_timeline(self, name, timeline):
        """Appends a new `(name, timeline)` to the end of the list."""
        if self.active_index == -1:
            self.active_index = 0
            self.active_timeline_name = name
            self.active_timeline = timeline
        self.timelines.append((name, timeline))

    def activate_previous(self):
        """Marks as active the previous `Timeline` if it exists."""
        new_index = self.active_index - 1
        if self._is_valid_index(new_index):
            self.active_index = new_index
    
    def activate_next(self):
        """Marks as active the next `Timeline` if it exists."""
        new_index = self.active_index + 1
        if self._is_valid_index(new_index):
            self.active_index = new_index

    def activate_first(self):
        if self.has_timelines():
            self.active_index = 0

    def activate_last(self):
        if self.has_timelines():
            self.active_index = len(self.timelines) - 1

    def _swap_timelines(self, one, other):
        """
        Given the indexes of two timelines `one` and `other`, it swaps the 
        (name, timeline) tuples contained in those positions.
        """
        if self._is_valid_index(one) and self._is_valid_index(other):
            self.timelines[one], self.timelines[other] = \
                    self.timelines[other], self.timelines[one]

    def shift_active_left(self):
        """Shifts the active buffer one position to the left."""
        active_index = self.active_index
        previous_index = active_index - 1
        if self._is_valid_index(previous_index):
            self._swap_timelines(previous_index, active_index)
            self.active_index = previous_index

    def shift_active_right(self):
        """Shifts the active buffer one position to the right."""
        active_index = self.active_index
        next_index = active_index + 1
        if self._is_valid_index(next_index):
            self._swap_timelines(active_index, next_index)
            self.active_index = next_index

    def shift_active_beggining(self):
        """Shifts the active buffer (if any) to the begginning of the list."""
        if self.has_timelines():
            first_index = 0
            self.timelines.insert(first_index, self.timelines[self.active_index])
            del self.timelines[self.active_index + 1]
            self.active_index = first_index

    def shift_active_end(self):
        """Shifts the active buffer (if any) to the begginning of the list."""
        if self.has_timelines():
            last_index = len(self.timelines)
            self.timelines.insert(last_index, self.timelines[self.active_index])
            self.delete_active_timeline()
            self.active_index = last_index - 1

    def delete_active_timeline(self):
        """
        Deletes the active timeline (if any) and shifts the active index 
        to the left.
        """
        if self.has_timelines():
            del self.timelines[self.active_index]
            if self.has_timelines() and self.active_index == 0:
                return
            self.active_index = self.active_index - 1

    def update_active_timeline(self):
        if self.has_timelines():
            _, tl = self.timelines[self.active_index]
            tl.update()

    def update_all(self):
        """Updates every `Timeline`."""
        for _, timeline in self.timelines:
            timeline.update()

    def delete_all(self):
        """Deletes every `Timeline`."""
        self.timelines = []

    def get_timelines(self):
        return [timeline for _, timeline in self.timelines]

    def get_timeline_names(self):
        return [name for name, _ in self.timelines]

    def __iter__(self):
        return self.timelines.__iter__()

    def __len__(self):
        return self.timelines.__len__()
