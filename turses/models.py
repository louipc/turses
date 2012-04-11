# -*- coding: utf-8 -*-

"""
turses.models
~~~~~~~~~~~~~

This module contains the Twitter entities represented in `turses`.
"""

import time
from functools import total_ordering
from bisect import insort

from .utils import html_unescape, timestamp_from_datetime

##
#  Helper functions
##

def is_DM(status):
    return status.__class__ == DirectMessage

def get_mentioned_for_reply(status):
    author = get_authors_username(status)
    mentioned = get_mentioned_usernames(status)
    mentioned.insert(0, author)

    prepend_at = lambda username: '@%s' % username
    return map(prepend_at, mentioned)

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
    return string.startswith('@') and len(string) > 1

def is_hashtag(string):
    return string.startswith('#') and len(string) > 1

def sanitize_username(username):
    is_legal_username_char = lambda char: char.isalnum()
    sanitized = filter(is_legal_username_char, username[1:])
    return sanitized

def get_mentioned_usernames(status):
    usernames = filter(is_username, status.text.split())
    return map(sanitize_username, usernames)

def get_hashtags(status):
    return filter(is_hashtag, status.text.split())

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


@total_ordering
class Status(object):
    """
    A Twitter status. 
    
    Api adapters must convert their representations to instances of this class.
    """

    # TODO make all arguments mandatory
    def __init__(self, 
                 id,
                 created_at,
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
                 
        self.id = id
        self.created_at = created_at
        self.user = user
        self.text = html_unescape(text)
        self.is_reply = is_reply
        self.is_retweet = is_retweet
        self.is_favorite = is_favorite
        self.retweet_count = retweet_count
        self.author = author

    # TODO: `datetime.datetime` object as `created_at` attributte and get
    #        rid off `created_at_in_seconds` attribute

    def get_relative_created_at(self):
        """Return a human readable string representing the posting time."""
        # This code is borrowed from `python-twitter` library
        fudge = 1.25
        delta  = long(time.time()) - timestamp_from_datetime(self.created_at)

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

    # magic

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        # statuses are ordered reversely by date
        return self.created_at > other.created_at


class DirectMessage(Status):
    """
    A Twitter direct message. 
    
    Api adapters must convert their representations to instances of this class.
    """

    def __init__(self,
                 id,
                 created_at,
                 sender_screen_name,
                 recipient_screen_name,
                 text):
        self.id = id
        self.created_at= created_at
        self.sender_screen_name = sender_screen_name
        self.recipient_screen_name = recipient_screen_name
        self.text = html_unescape(text)


class List(object):
    """
    A Twitter list. 
    
    Api adapters must convert their representations to instances of this class.
    """
    
    def __init__(self,
                 id,
                 owner,
                 created_at,
                 name,
                 description,
                 member_count,
                 subscriber_count,
                 private=False,):
        self.id = id
        self.owner = owner
        self.created_at = created_at
        self.name = name
        self.description = description
        self.member_count = member_count
        self.subscriber_count = subscriber_count
        self.private = private
                 

class ActiveList(object):
    """
    A list that contains an 'active' element. 
    
    This class implements some functions but the subclasses must define 
    `get_active`, `is_valid_index` and `activate_last` methods.
    """
    NULL_INDEX = -1

    def __init__(self):
        self.active_index = self.NULL_INDEX

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
            self.active_index = self.NULL_INDEX

    def activate_last(self):
        raise NotImplementedError


class UnsortedActiveList(ActiveList):
    """
    An `ActiveList` in which the 'active' element can be shifted position by
    position, to the begging and to the end. 
    
    Subclasses must implement all the provided methods.
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

    One of the elements of the timeline is the 'active' since `Timeline`
    extends `ActiveList`.
    """

    def __init__(self, 
                 name='',
                 statuses=None,
                 update_function=None,
                 update_function_args=None):
        ActiveList.__init__(self)
        self.name = name

        if statuses:
            # sort when first inserting statuses
            key = lambda status: status.created_at
            self.statuses = sorted(statuses,
                                   key=key,
                                   reverse=True)
            self.active_index = 0
            self._mark_read()
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
        if new_status in self.statuses:
            return

        if self.active_index == self.NULL_INDEX:
            self.active_index = 0

        # keep the same tweet as the active when inserting statuses
        active = self.get_active()
        is_more_recent_status = lambda a, b: a.created_at < b.created_at

        if active and is_more_recent_status(active, new_status):
            self.activate_next()

        insort(self.statuses, new_status)

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
        self.active_index = self.NULL_INDEX
        self.statuses = []

    def get_newer_than(self, datetime):
        """Return the statuses that are more recent than `datetime`."""
        newer = lambda status : status.created_at > datetime
        return filter(newer, self.statuses)

    def update(self):
        # TODO: use a generator (?)
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

    def get_unread_count(self):
        def one_if_unread(tweet):
            readed = lambda tweet: getattr(tweet, 'read', False)
            return 0 if readed(tweet) else 1

        return sum([one_if_unread(tweet) for tweet in self.statuses])

    # magic

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
            self.active_index = self.NULL_INDEX
        return False

    def activate_previous(self):
        ActiveList.activate_previous(self)
        self.mark_active_as_read()
    
    def activate_next(self):
        ActiveList.activate_next(self)
        self.mark_active_as_read()

    def activate_first(self):
        ActiveList.activate_first(self)
        self.mark_active_as_read()

    def activate_last(self):
        if self.statuses:
            self.active_index = len(self.statuses) - 1
            self.mark_active_as_read()
        else:
            self.active_index = self.NULL_INDEX

    # utils

    def mark_active_as_read(self):
        """Set active status' `read` attribute to `True`."""
        active_status = self.get_active()
        if active_status:
            active_status.read = True


class TimelineList(UnsortedActiveList):
    """
    A list of `Timeline` objects in which only one is the 'active'
    timeline.
    """

    def __init__(self):
        UnsortedActiveList.__init__(self)
        self.timelines = []

    def has_timelines(self):
        return self.active_index !=  self.NULL_INDEX and self.timelines

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

    def get_active_status(self):
        if self.has_timelines():
            active_timeline = self.get_active_timeline()
            return active_timeline.get_active()

    def append_timeline(self, timeline):
        """Appends a new `Timeline` to the end of the list."""
        if self.active_index == -1:
            self.active_index = 0
            # `timeline` becomes the active
            self.timelines.append(timeline)
            self._mark_read()
            return
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

    def get_unread_counts(self):
        return [timeline.get_unread_count() for timeline in self.timelines]

    # magic

    def __iter__(self):
        return self.timelines.__iter__()

    def __len__(self):
        return self.timelines.__len__()

    # from `UnsortedActiveList`
    
    def get_active(self):
        return self.get_active_timeline()

    def is_valid_index(self, index):
        return index >= 0 and index < len(self.timelines)

    def activate_previous(self):
        UnsortedActiveList.activate_previous(self)
        self._mark_read()
    
    def activate_next(self):
        UnsortedActiveList.activate_next(self)
        self._mark_read()

    def activate_first(self):
        UnsortedActiveList.activate_first(self)
        self._mark_read()

    def activate_last(self):
        if self.has_timelines():
            self.active_index = len(self.timelines) - 1
        self._mark_read()

    def _swap_timelines(self, one, other):
        """
        Given the indexes of two timelines `one` and `other`, it swaps the 
        `Timeline` objects contained in those positions.
        """
        if self.is_valid_index(one) and self.is_valid_index(other):
            self.timelines[one], self.timelines[other] = \
                    self.timelines[other], self.timelines[one]

    def _mark_read(self):
        if self.has_timelines():
            active_timeline = self.get_active_timeline()
            active_timeline.mark_active_as_read()

    def get_focused_status(self):
        active_timeline = self.get_active_timeline()
        return active_timeline.get_active()

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


class VisibleTimelineList(TimelineList):
    """
    A `TimelineList` that tracks a number of `visible` timelines. It also has
    an `active` timeline, which has to be within the visible ones.
    """

    def __init__(self, *args, **kwargs):
        TimelineList.__init__(self, *args, **kwargs)
        self.visible = []

    def expand_visible_previous(self):
        if not self.visible:
            return

        self.visible.sort()
        lowest = self.visible[0]
        previous = lowest - 1
        if self.is_valid_index(previous):
            self.visible.insert(0, previous)

    def expand_visible_next(self):
        if not self.visible:
            return 

        self.visible.sort()
        highest = self.visible[-1]
        next = highest + 1
        if self.is_valid_index(next):
            self.visible.append(next)

    def shrink_visible_beggining(self):
        self.visible.sort()
        try:
            first = self.visible.pop(0)
            # if the active is the first one does not change
            if first == self.active_index:
                self.visible.insert(0, first)
        except IndexError:
            pass

    def shrink_visible_end(self):
        self.visible.sort()
        try:
            last = self.visible.pop()
            # if the active is the last one does not change
            if last == self.active_index:
                self.visible.append(last)
        except IndexError:
            pass

    def get_visible_indexes(self):
        return self.visible

    # TODO: rename this
    def get_visible_timeline_relative_index(self):
        return self.visible.index(self.active_index)

    # from `TimelineList`

    def append_timeline(self, timeline):
        # when appending a timeline is visible only if the `TimelineList` was empty
        if self.active_index == self.NULL_INDEX:
            self.visible = [0]
        TimelineList.append_timeline(self, timeline)

    def delete_active_timeline(self):
        try:
            self.visible.remove(self.active_index)
        except ValueError:
            pass
        finally:
            TimelineList.delete_active_timeline(self)
        self._set_active_as_visible()

    def get_visible_timelines(self):
        return [self.timelines[i] for i in self.visible]

    def _set_active_as_visible(self):
        if self.active_index not in self.visible:
            self.visible = [self.active_index]

    def activate_previous(self):
        TimelineList.activate_previous(self)
        self._set_active_as_visible()
    
    def activate_next(self):
        TimelineList.activate_next(self)
        self._set_active_as_visible()

    def activate_first(self):
        TimelineList.activate_first(self)
        self._set_active_as_visible()

    def activate_last(self):
        TimelineList.activate_last(self)
        self._set_active_as_visible()

    def shift_active_previous(self):
        TimelineList.shift_active_previous(self)
        self._set_active_as_visible()

    def shift_active_next(self):
        TimelineList.shift_active_next(self)
        self._set_active_as_visible()

    def shift_active_beggining(self):
        TimelineList.shift_active_beggining(self)
        self._set_active_as_visible()

    def shift_active_end(self):
        TimelineList.shift_active_end(self)
        self._set_active_as_visible()
