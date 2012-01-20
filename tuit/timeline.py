# -*- coding: utf-8 -*-
#
# Copyright © 2011 Nicolas Paris <nicolas.caen@gmail.com>
# Copyright © 2012 Alejandro Gómez <alejandroogomez@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


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
        return self.update()

    def add_new_statuses(self, new_statuses):
        """Adds the given new statuses to the status list of the Timeline."""
        for status in new_statuses:
            if status not in self.statuses:
                self.statuses.insert(0, status)

    def __len__(self):
        return len(self.statuses)
