# -*- coding: utf-8 -*-

"""
turses.models
~~~~~~~~~~~~~

This module contains the Twitter entities represented in `turses`.
"""

import time
import re
from functools import total_ordering
from bisect import insort

from turses.utils import (html_unescape, timestamp_from_datetime,
                          wrap_exceptions, is_url)


##
#  Helpers
##

username_regex = re.compile(r'[A-Za-z0-9_]+')

hashtag_regex = re.compile(r'#.+')

prepend_at = lambda username: '@%s' % username

STATUS_URL_TEMPLATE = 'https://twitter.com/#!/{user}/status/{id}'


def get_status_url(status):
    return STATUS_URL_TEMPLATE.format(user=status.user, id=status.id)

def is_DM(status):
    return status.__class__ == DirectMessage


def get_mentioned_usernames(status):
    """
    Return mentioned usernames in `status` without '@'.
    """
    usernames = []
    for word in status.text.split():
        if len(word) > 1 and word.startswith('@'):
            word.strip('@')
            usernames.append(word)
    return map(sanitize_username, usernames)


def get_mentioned_for_reply(status):
    """
    Return a list containing the author of `status` and all the mentioned
    usernames prepended with '@'.
    """
    author = get_authors_username(status)
    mentioned = get_mentioned_usernames(status)
    mentioned.insert(0, author)

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


def get_dm_recipients_username(sender, status):
    """
    Return the recipient for a Direct Message depending on what `status`
    is.

    If is a `turses.models.Status` and sender != `status.user` I will return
    `status.user`.

    If is a `turses.models.DirectMessage` I will return the username that
    is not `sender` looking at the DMs sender and recipient.

    Otherwise I return `None`.
    """
    username = None
    if is_DM(status):
        users = [status.sender_screen_name,
                 status.recipient_screen_name]
        if sender in users:
            users.pop(users.index(sender))
            username = users.pop()
    elif status.user != sender:
        username = status.user
    return username


def is_username(username):
    """
    Return `True` if `username` is a valid Twitter username, `False`
    otherwise.
    """
    match = username_regex.match(username)
    if match:
        return match.start() == 0 and match.end() == len(username)
    return False


def is_hashtag(hashtag):
    """
    Return `True` if `hashtag` is a valid Twitter hashtag, `False`
    otherwise.
    """
    match = hashtag_regex.match(hashtag)
    if match:
        return match.start() == 0 and match.end() == len(hashtag)
    return False


def sanitize_username(username):
    """
    Return `username` with illegal characters for a Twitter username
    striped.
    """
    sanitized = filter(is_username, username)
    return sanitized


def get_hashtags(status):
    """
    Return a list of hashtags encountered in `status`.
    """
    return filter(is_hashtag, status.text.split())


def is_valid_status_text(text):
    """Checks the validity of a status text."""
    return text and len(text) <= 140


def is_valid_search_text(text):
    """Checks the validity of a search text."""
    return bool(text)


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
                 retweeted_status=None,
                 retweet_count=0,
                 author='',
                 entities=None):
        self.id = id
        self.created_at = created_at
        self.user = user
        self.text = html_unescape(text)
        self.is_reply = is_reply
        self.is_retweet = is_retweet
        self.is_favorite = is_favorite
        self.retweet_count = retweet_count
        self.retweeted_status = retweeted_status
        self.author = author
        self.entities = {} if entities is None else entities

    def get_relative_created_at(self):
        """Return a human readable string representing the posting time."""
        # This code is borrowed from `python-twitter` library
        fudge = 1.25
        delta = long(time.time()) - timestamp_from_datetime(self.created_at)

        if delta < (1 * fudge):
            return "a second ago"
        elif delta < (60 * (1 / fudge)):
            return "%d seconds ago" % (delta)
        elif delta < (60 * fudge):
            return "a minute ago"
        elif delta < (60 * 60 * (1 / fudge)):
            return "%d minutes ago" % (delta / 60)
        elif delta < (60 * 60 * fudge) or delta / (60 * 60) == 1:
            return "an hour ago"
        elif delta < (60 * 60 * 24 * (1 / fudge)):
            return "%d hours ago" % (delta / (60 * 60))
        elif delta < (60 * 60 * 24 * fudge) or delta / (60 * 60 * 24) == 1:
            return "a day ago"
        else:
            return "%d days ago" % (delta / (60 * 60 * 24))

    # TODO: refactor this aberration 
    def map_attributes(self, hashtag, attag, url):
        """
        Return a list of strings and tuples for hashtag, attag and url entities.

        For a hashtag, its tuple would be (`hashtag`, text). 

        >>> from datetime import datetime
        >>> s = Status(id=0, 
        ...            created_at=datetime.now(),
        ...            user='dialelo',
        ...            text='I love #Python',)
        >>> s.map_attributes('hashtag', 'attag', 'url')
        ['I love ', ('hashtag', '#Python')]
        """
        # Favorites don't include any entities so we parse the status
        # text manually.
        if not getattr(self, 'entities', False):
            text = self.retweeted_status.text if self.is_retweet else self.text
            return self.parse_attributes(text,
                                         hashtag,
                                         attag,
                                         url)
        elif getattr(self, 'is_retweet', False):
            return self.retweeted_status.map_attributes(hashtag, attag, url)

        def map_attr(attr, entity_list):
            """
            Return a list with (`attr`, string) tuples for each string in 
            `entity_list`.
            """
            attr_mappings = []
            for entity in entity_list:
                # urls are a special case, we change the URL shortened by
                # Twitter (`http://t.co/*`) by the URL returned in `display_url`
                indices = entity.get('indices')
                url = entity.get('display_url', False)

                if url:
                    mapping = (attr, indices, url)
                else:
                    mapping = (attr, indices)
                attr_mappings.append(mapping)
            return attr_mappings

        attr_mappings = []

        # TODO: dry
        usernames = self.entities.get('user_mentions', [])
        usernames_attrs = map_attr(attag, usernames)
        attr_mappings.extend(usernames_attrs)

        hashtags = self.entities.get('hashtags', [])
        hashtags_attrs = map_attr(hashtag, hashtags)
        attr_mappings.extend(hashtags_attrs)

        urls = self.entities.get('urls', [])
        urls_attrs = map_attr(url, urls)
        attr_mappings.extend(urls_attrs)

        media = self.entities.get('media', [])
        media_attrs = map_attr(url, media)
        attr_mappings.extend(media_attrs)

        # sort mappings to split the text in order
        attr_mappings.sort(key=lambda mapping: mapping[1][0])

        text = []
        status_text = unicode(self.text)
        index = 0
        for mapping in attr_mappings:
            attr = mapping[0]
            starts, ends = mapping[1]
            if attr == url and len(mapping) == 3:
                ## if the text is a url and a third element is included in the
                ## tuple; the third element is the original URL
                entity_text = mapping[2]
            else:
                entity_text = status_text[starts:ends]

            # append normal text before special entity
            normal_text = status_text[index:starts]
            if normal_text:
               text.append(normal_text)

            # append text with attr
            text_with_attr = (attr, entity_text)
            text.append(text_with_attr)

            # update index
            index = ends
        normal_text = status_text[index:]
        if normal_text:
            text.append(normal_text)

        return text

    def parse_attributes(self, text, hashtag, attag, url):
        words = text.split()

        def apply_attribute(string):
            if is_hashtag(string):
                return (hashtag, string)
            elif string.startswith('@') and is_username(string[1:-1]):
                # FIXME: we can lose some characters here..
                username = sanitize_username(string)
                return (attag, '@' + username)
            elif is_url(string):
                return  (url, string)
            else:
                return string

        text = map(apply_attribute, words)
        tweet = []
        tweet.append(text[0])
        for word in text[1:]:
            tweet.append(' ')
            tweet.append(word)
        return tweet

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
                 text,
                 entities=None):
        self.id = id
        self.created_at = created_at
        self.sender_screen_name = sender_screen_name
        self.recipient_screen_name = recipient_screen_name
        self.text = html_unescape(text)
        self.entities = entities


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
                 update_function_args=None,
                 update_function_kwargs=None):
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

        self.update_function_args = None
        self.update_function_kwargs = None

        if update_function_args or update_function_kwargs:
            self._extract_args_and_kwargs(update_function_args,
                                          update_function_kwargs)

    def _extract_args_and_kwargs(self, update_args, update_kwargs):
        is_dict = lambda d: isinstance(d, dict)
        is_tuple = lambda t: isinstance(t, tuple)
        is_list = lambda l: isinstance(l, list)

        if is_tuple(update_args):
            # multiple arguments in a tuple
            args = list(update_args)
            self.update_function_args = args
        elif is_list(update_args) or update_args:
            # list of args or one arg
            self.update_function_args = update_args

        if is_dict(update_kwargs):
            # dict with kwargs
            self.update_function_kwargs = update_kwargs

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
        newer = lambda status: status.created_at > datetime
        return filter(newer, self.statuses)

    @wrap_exceptions
    def update(self):
        # TODO: use a generator (?)
        if not self.update_function:
            return

        args = self.update_function_args
        kwargs = self.update_function_kwargs

        if args is not None and kwargs is not None:
            if not isinstance(args, list):
                args = [self.update_function_args]

            new_statuses = self.update_function(*args, **kwargs)

        elif args:
            if not isinstance(args, list):
                args = [self.update_function_args]
            new_statuses = self.update_function(*args)
        elif kwargs:
            new_statuses = self.update_function(**kwargs)
        else:
            new_statuses = self.update_function()
        self.add_statuses(new_statuses)

    def update_with_extra_kwargs(self, **extra_kwargs):
        if not self.update_function:
            return

        update_args = self.update_function_args
        update_kwargs = self.update_function_kwargs

        if isinstance(update_args, list):
            args = update_args
        elif update_args:
            args = [update_args]

        if update_kwargs:
            kwargs = update_kwargs.copy()
            kwargs.update(extra_kwargs)
        else:
            kwargs = extra_kwargs

        if update_args:
            # both args and kwargs
            new_statuses = self.update_function(*args, **kwargs)
        else:
            # kwargs only
            new_statuses = self.update_function(**kwargs)

        self.add_statuses(new_statuses)

    def get_unread_count(self):
        def one_if_unread(tweet):
            if hasattr(tweet, 'read') and tweet.read:
                return 0
            return 1

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

    def mark_all_as_read(self):
        for status in self.statuses:
            status.read = True


class TimelineList(UnsortedActiveList):
    """
    A list of `Timeline` objects in which only one is the 'active'
    timeline.
    """

    def __init__(self):
        UnsortedActiveList.__init__(self)
        self.timelines = []

    def has_timelines(self):
        return self.active_index != self.NULL_INDEX and self.timelines

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
