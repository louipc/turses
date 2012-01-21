###############################################################################
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import re

from util import html_unescape

from twitter import Status as BaseStatus

retweet_re = re.compile('^RT @\w+:')

class Status(BaseStatus):
    def __init__(self, status):
        self.status = status
        self.status.text = html_unescape(self.status.text)

    @property
    def id(self):
        return self.status.id

    def get_time(self):
        """
        Convert the time format given by the api to something more
        readable.
        """
        try:
            result =  self.status.GetRelativeCreatedAt()
        except AttributeError:
            hour = time.gmtime(self.status.GetCreatedAtInSeconds() - time.altzone)
            result = time.strftime('%H:%M', hour)
        return result

    def get_text(self):
        return self.status.text

    def get_source(self):
        source = ''
        if hasattr(self.status, 'source'):
            source = get_source(self.status.source)
        return source

    def get_username(self):
        if hasattr(self.status, 'user'):
            username = self.status.user.screen_name
        else:
            # Used for direct messages
            username = self.status.sender_screen_name
        return username

    def get_retweet_count(self):
        if hasattr(self.status, 'retweet_count'):
            return self.status.retweet_count

    def is_retweet(self):
        return bool(retweet_re.match(status.text))

    def is_reply(self, status):
        if hasattr(self.status, 'in_reply_to_screen_name'):
            reply = self.status.in_reply_to_screen_name
            if reply:
                return True
        return False

    def origin_of_retweet(self, status):
        """
        When its a retweet, return the first person who tweeted it,
        not the retweeter.
        """
        origin = status.text
        origin = origin[4:]
        origin = origin.split(':')[0]
        origin = str(origin)
        return origin


class TimelineException(Exception):
    pass


class Timeline(object):
    """Maintains a list of Twitter statuses."""

    def __init__(self, update_function=None):
        self.statuses = []
        self.update = update_function

    def update_timeline(self):
        """Updates the Timeline with new statuses."""
        new_statuses = self.get_new_statuses()
        if new_statuses:
            new_statuses.reverse()
            self.add_new_statuses(new_statuses)

    def get_new_statuses(self):
        """
        If a function to update the Timeline has been specified, it fetches the
        new statuses calling it. If not, raises a `TimelineException`.
        """
        if self.update is None: 
            raise TimelineException("The timeline cannot be updated without " + 
                                    "specifying an update function.")
        return [Status(status) for status in self.update()]

    def add_new_statuses(self, new_statuses):
        """Adds the given new statuses to the status list of the Timeline."""
        for status in new_statuses:
            if status not in self.statuses:
                self.statuses.insert(0, status)
        if self.update_callback:
            self.update_callback(new_statuses)

    def set_update_callback(self, callback):
        self.update_callback = callback

    def __len__(self):
        return len(self.statuses)

    def __iter__(self):
        return self.statuses.__iter__()
