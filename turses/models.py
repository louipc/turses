###############################################################################
#                               coding=utf-8                                  #
#            Copyright (c) 2012 turses contributors. See AUTHORS.             #
#         Licensed under the GPL License. See LICENSE for full details.       #
###############################################################################

import re
from datetime import datetime
import time

from .util import html_unescape, timestamp_from_datetime


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
    """Return the original author's username of the given status."""
    if is_DM(status):
        username = status.sender_screen_name
    elif status.is_retweet:
        username = status.author
    else:
        username = status.user

    return username

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
    """
    Programs representation of a Twitter user. Api adapters must convert
    their representations to instances of this class.
    """

    def __init__(self,
                 screen_name):
        self.screen_name = screen_name


class Status(object):
    """
    Programs representation of a Twitter status. Api adapters must convert
    their representations to instances of this class.
    """

    # TODO make all arguments mandatory
    def __init__(self, 
                 created_at_in_seconds,
                 id,
                 user,
                 text,
                 is_reply=False,
                 is_retweet=False,
                 is_favorite=False,
                 # for replies
                 in_reply_to_user='',
                 # for retweets
                 retweet_count=0,
                 author='',):
                 
        self.created_at_in_seconds = created_at_in_seconds
        self.user = user
        self.id = id
        self.text = html_unescape(text)
        self.is_reply = is_reply
        self.is_retweet = is_retweet
        self.is_favorite = is_favorite
        self.retweet_count = retweet_count
        self.author = author

    def get_relative_created_at(self):
        """Return a human readable string representing the posting time."""
        # This code is borrowed from `python-twitter` library
        fudge = 1.25
        delta  = long(time.time()) - long(self.created_at_in_seconds)

        if delta < (1 * fudge):
          return "about a second ago"
        elif delta < (60 * (1/fudge)):
          return "about %d seconds ago" % (delta)
        elif delta < (60 * fudge):
          return "about a minute ago"
        elif delta < (60 * 60 * (1/fudge)):
          return "about %d minutes ago" % (delta / 60)
        elif delta < (60 * 60 * fudge) or delta / (60 * 60) == 1:
          return "about an hour ago"
        elif delta < (60 * 60 * 24 * (1/fudge)):
          return "about %d hours ago" % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge) or delta / (60 * 60 * 24) == 1:
          return "about a day ago"
        else:
          return "about %d days ago" % (delta / (60 * 60 * 24))

    def __eq__(self, other):
        return self.id == other.id


class DirectMessage(Status):
    """
    Programs representation of a Twitter direct message. Api adapters must 
    convert their representations to instances of this class.
    """

    def __init__(self,
                 id,
                 created_at_in_seconds,
                 sender_screen_name,
                 recipient_screen_name,
                 text):
        self.id = id
        self.created_at_in_seconds = created_at_in_seconds
        self.sender_screen_name = sender_screen_name
        self.recipient_screen_name = recipient_screen_name
        self.text = html_unescape(text)


class List(object):
    # TODO
    pass


class ActiveList(object):
    """
    A list that contains an 'active' element. This class implements some
    functions but the subclasses must define `get_active`, `is_valid_index` 
    and `activate_last` methods.
    """
    NULL = -1

    def __init__(self):
        self.active_index = self.NULL

    def get_active(self):
        raise NotImplementedError

    def is_valid_index(self, index):
        raise NotImplementedError

    def activate_previous(self):
        """Marks as active the previous `Timeline` if it exists."""
        new_index = self.active_index - 1
        if self.is_valid_index(new_index):
            self.active_index = new_index
    
    def activate_next(self):
        """Marks as active the next `Timeline` if it exists."""
        new_index = self.active_index + 1
        if self.is_valid_index(new_index):
            self.active_index = new_index

    def activate_first(self):
        if self.is_valid_index(0):
            self.active_index = 0
        else:
            self.active_index = self.NULL

    def activate_last(self):
        raise NotImplementedError


class UnsortedActiveList(ActiveList):
    """
    An `ActiveList` in which the 'active' element can be shifted position by
    position, to the begging and to the end. 
    
    The subclass must implement all the provided methods.
    """

    def shift_active_previous(self):
        """Shifts the active timeline one position to the left."""
        raise NotImplementedError

    def shift_active_next(self):
        """Shifts the active timeline one position to the right."""
        raise NotImplementedError

    def shift_active_beggining(self):
        """Shifts the active timeline (if any) to the begginning of the list."""
        raise NotImplementedError

    def shift_active_end(self):
        """Shifts the active timeline (if any) to the begginning of the list."""
        raise NotImplementedError


class Timeline(ActiveList):
    """
    List of Twitter statuses ordered reversely by date. Optionally with
    a name, a function that updates the current timeline and its arguments.

    One of the elements of the timeline is the 'active'.
    """

    # TODO make possible to pass dicts as **kwargs in `update_function_args`
    def __init__(self, 
                 name='',
                 statuses=None,
                 update_function=None,
                 update_function_args=None):
        ActiveList.__init__(self)
        self.name = name
        # key for sorting
        self._key = lambda status: status.created_at_in_seconds
        if statuses:
            self.statuses = sorted(statuses,
                                   key=self._key,
                                   reverse=True)
            self.active_index = 0
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
            if self.active_index == self.NULL:
                self.active_index = 0
            # TODO: keep cursor in same tweet when inserting statuses (?)
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
        self.active_index = self.NULL
        self.statuses = []

    def get_newer_than(self, datetime):
        """Return the statuses that are more recent than `datetime`."""
        timestamp = timestamp_from_datetime(datetime)
        newer = lambda status : status.created_at_in_seconds > timestamp
        return filter(newer, self.statuses)

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

    # from `ActiveList`

    def get_active(self):
        if self.statuses and self.is_valid_index(self.active_index):
            return self.statuses[self.active_index]

    def is_valid_index(self, index):
        if self.statuses:
            return index >= 0 and index < len(self.statuses)
        else:
            self.active_index = self.NULL
        return False

    def activate_last(self):
        if self.statuses:
            self.active_index = len(self.statuses) - 1
        else:
            self.active_index = self.NULL


class TimelineList(UnsortedActiveList):
    """
    A list of `Timeline` objects in which only one is the 'active'
    timeline.
    """

    def __init__(self):
        UnsortedActiveList.__init__(self)
        self.timelines = []

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

    def get_focused_status(self):
        if self.has_timelines():
            active_timeline = self.get_active_timeline()
            return active_timeline.get_active()

    def append_timeline(self, timeline):
        """Appends a new `Timeline` to the end of the list."""
        if self.active_index == -1:
            self.active_index = 0
        self.timelines.append(timeline)

    def delete_active_timeline(self):
        """
        Deletes the active timeline (if any) and shifts the active index 
        to the right.
        """
        if self.has_timelines():
            del self.timelines[self.active_index]
            if self.is_valid_index(self.active_index):
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

    # from `UnsortedActiveList`
    
    def get_active(self):
        return self.get_active_timeline()

    def is_valid_index(self, index):
        return index >= 0 and index < len(self.timelines)

    def activate_last(self):
        if self.has_timelines():
            self.active_index = len(self.timelines) - 1

    def _swap_timelines(self, one, other):
        """
        Given the indexes of two timelines `one` and `other`, it swaps the 
        `Timeline` objects contained in those positions.
        """
        if self.is_valid_index(one) and self.is_valid_index(other):
            self.timelines[one], self.timelines[other] = \
                    self.timelines[other], self.timelines[one]

    def shift_active_previous(self):
        active_index = self.active_index
        previous_index = active_index - 1
        if self.is_valid_index(previous_index):
            self._swap_timelines(previous_index, active_index)
            self.active_index = previous_index

    def shift_active_next(self):
        active_index = self.active_index
        next_index = active_index + 1
        if self.is_valid_index(next_index):
            self._swap_timelines(active_index, next_index)
            self.active_index = next_index

    def shift_active_beggining(self):
        if self.has_timelines():
            first_index = 0
            self.timelines.insert(first_index, self.timelines[self.active_index])
            del self.timelines[self.active_index + 1]
            self.active_index = first_index

    def shift_active_end(self):
        if self.has_timelines():
            last_index = len(self.timelines)
            self.timelines.insert(last_index, self.timelines[self.active_index])
            self.delete_active_timeline()
            self.active_index = last_index - 1
