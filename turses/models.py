###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import re
from datetime import datetime


retweet_re = re.compile('^RT @\w+:')

##
#  Helper functions
##

def datetime_from_status(status):
    """Converts a date on a Twitter status to a `datetime` object."""
    # TODO
    #seconds = status.GetCreatedAtInSeconds()
    return datetime.utcfromtimestamp(0)

def is_more_recent(status, datetime):
    """Checks wether `status.created_at` is newer than `datetime`."""
    created_at = datetime_from_status(status)
    return created_at > datetime

def is_tweet(status):
    return status.__class__ == Status

def is_retweet(status):
    return bool(retweet_re.match(status.text))

def is_DM(status):
    return status.__class__ == DirectMessage

def get_authors_username(status):
    """Returns the original author's username of the given status."""
    if is_DM(status):
        username = status.sender_screen_name
    else:
        username = status.user.screen_name
    return ''.join(['@', username])

def is_username(string):
    return string.startswith('@')

def sanitize_username(username):
    is_legal_username_char = lambda char: char.isalnum()
    sanitized = filter(is_legal_username_char, username[1:])
    return ''.join(['@', sanitized])

def get_mentioned_usernames(status):
    usernames = filter(is_username, status.text.split())
    return map(sanitize_username, usernames)

def is_valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= 140

def is_valid_search_text(text):
    """Checks the validity of a search text."""
    return bool(text)

def is_valid_username(username):
    return username.isalnum()


##
#  Classes
##


class User(object):
    def __init__(self,
                 screen_name):
        self.screen_name = screen_name


class Status(object):

    def __init__(self, user):
        self.user = user


class DirectMessage(object):

    def __init__(self,
                 id,
                 sender_screen_name,
                 text):
        self.id = id
        self.sender_screen_name = sender_screen_name
        self.text = text


class Timeline(object):
    """
    List of Twitter statuses ordered reversely by date. Optionally with
    a name, a function that updates the current timeline and its arguments.
    """

    # TODO make possible to pass dicts as **kwargs in `update_function_args`
    def __init__(self, 
                 name='',
                 statuses=None,
                 update_function=None,
                 update_function_args=None):
        self.name = name
        # key for sorting
        self._key = lambda status: datetime_from_status(status)
        if statuses:
            self.statuses = sorted(statuses,
                                   key=self._key,
                                   reverse=True)
        else:
            self.statuses = []
        self.update_function = update_function
        if update_function_args:
            self._extract_args_and_kargs(update_function_args)
        else:
            self.update_function_args = None
            self.update_function_kargs = None

    def _extract_args_and_kargs(self, update_args):
        self.update_function_args = None
        self.update_function_kargs = None
        isdict = lambda d : isinstance(d, dict)
        if isinstance(update_args, tuple):
            # multiple arguments
            args = list(update_args)
            kargs = args.pop()
            if isdict(kargs):
                self.update_function_args = args
                self.update_function_kargs = kargs
            else:
                args.append(kargs)
                self.update_function_args =  args
        else:
            # one argument (possibly kargs)
            if isinstance(update_args, dict):
                # kargs
                self.update_function_kargs = update_args
            else:
                # args
                self.update_function_args = update_args

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
        if not new_statuses:
            return
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
        if not self.update_function:
            return
        if self.update_function_args and self.update_function_kargs:
            args = list(self.update_function_args)
            args.append(self.update_function_kargs)
            new_statuses = self.update_function(tuple(args))
        elif self.update_function_args:
            if isinstance(self.update_function_args, list):
                args = tuple(self.update_function_args)
            else:
                args = self.update_function_args
            new_statuses = self.update_function(args)
        elif self.update_function_kargs:
            new_statuses = self.update_function(self.update_function_kargs)
        else:
            new_statuses = self.update_function()
        self.add_statuses(new_statuses)

    def __len__(self):
        return len(self.statuses)

    def __iter__(self):
        return self.statuses.__iter__()

    def __getitem__(self, i):
        return self.statuses[i]


class TimelineList(object):
    """
    A list of `Timeline` objects in which only one is the 'active'
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
            timeline = self.timelines[self.active_index]
            return timeline.name
        else:
            raise Exception("There are no timelines in the list")

    def get_active_timeline(self):
        if self.has_timelines():
            timeline = self.timelines[self.active_index]
            return timeline
        else:
            raise Exception("There are no timelines in the list")

    def append_timeline(self, timeline):
        """Appends a new `Timeline` to the end of the list."""
        if self.active_index == -1:
            self.active_index = 0
        self.timelines.append(timeline)

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
        `Timeline` objects contained in those positions.
        """
        if self._is_valid_index(one) and self._is_valid_index(other):
            self.timelines[one], self.timelines[other] = \
                    self.timelines[other], self.timelines[one]

    def shift_active_left(self):
        """Shifts the active timeline one position to the left."""
        active_index = self.active_index
        previous_index = active_index - 1
        if self._is_valid_index(previous_index):
            self._swap_timelines(previous_index, active_index)
            self.active_index = previous_index

    def shift_active_right(self):
        """Shifts the active timeline one position to the right."""
        active_index = self.active_index
        next_index = active_index + 1
        if self._is_valid_index(next_index):
            self._swap_timelines(active_index, next_index)
            self.active_index = next_index

    def shift_active_beggining(self):
        """Shifts the active timeline (if any) to the begginning of the list."""
        if self.has_timelines():
            first_index = 0
            self.timelines.insert(first_index, self.timelines[self.active_index])
            del self.timelines[self.active_index + 1]
            self.active_index = first_index

    def shift_active_end(self):
        """Shifts the active timeline (if any) to the begginning of the list."""
        if self.has_timelines():
            last_index = len(self.timelines)
            self.timelines.insert(last_index, self.timelines[self.active_index])
            self.delete_active_timeline()
            self.active_index = last_index - 1

    def delete_active_timeline(self):
        """
        Deletes the active timeline (if any) and shifts the active index 
        to the right.
        """
        if self.has_timelines():
            del self.timelines[self.active_index]
            if self._is_valid_index(self.active_index):
                pass
            else:
                self.active_index -= 1

    def update_active_timeline(self):
        if self.has_timelines():
            timeline = self.timelines[self.active_index]
            timeline.update()

    def update_all(self):
        """Updates every `Timeline`."""
        for timeline in self.timelines:
            timeline.update()

    def delete_all(self):
        """Deletes every `Timeline`."""
        self.active_index = -1
        self.timelines = []

    def get_timelines(self):
        return self.timelines

    def get_timeline_names(self):
        return [timeline.name for timeline in self.timelines]

    def __iter__(self):
        return self.timelines.__iter__()

    def __len__(self):
        return self.timelines.__len__()
