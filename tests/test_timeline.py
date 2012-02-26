###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('../')
import unittest
from datetime import datetime

from mock import MagicMock
from twitter import Status

from turses.timeline import Timeline, NamedTimelineList

class TimelineTest(unittest.TestCase):
    def setUp(self):
        self.timeline = Timeline()
        self.timeline.clear()
        self.assertEqual(len(self.timeline), 0)

    def _create_status_with_id_and_datetime(self, id, datetime):
        created_at = datetime.strftime('%a %b %d %H:%M:%S +0000 %Y')
        return Status(created_at=created_at, id=id,)

    def test_unique_statuses_in_timeline(self):
        self.assertEqual(len(self.timeline), 0)
        # create and add the status
        status = self._create_status_with_id_and_datetime(1, datetime.now())
        self.timeline.add_status(status)
        self.assertEqual(len(self.timeline), 1)
        # check that adding more than once does not duplicate element
        self.timeline.add_status(status)
        self.assertEqual(len(self.timeline), 1)

    def test_insert_different_statuses(self):
        old_status = self._create_status_with_id_and_datetime(1, 
                                                              datetime(1988, 12, 19))
        new_status = self._create_status_with_id_and_datetime(2, 
                                                              datetime.now())
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(len(self.timeline), 2)

    def test_insert_different_statuses_individually(self):
        old_status = self._create_status_with_id_and_datetime(1, 
                                                              datetime(1988, 12, 19))
        new_status = self._create_status_with_id_and_datetime(2, 
                                                              datetime.now())
        self.timeline.add_status(old_status)
        self.assertEqual(len(self.timeline), 1)
        self.timeline.add_status(new_status)
        self.assertEqual(len(self.timeline), 2)

    def test_statuses_ordered_reversely_by_date(self):
        old_status = self._create_status_with_id_and_datetime(1, 
                                                              datetime(1988, 12, 19))
        new_status = self._create_status_with_id_and_datetime(2, 
                                                              datetime.now())
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(self.timeline[0], new_status)
        self.assertEqual(self.timeline[1], old_status)

    def test_get_newer_than(self):
        old_created_at = datetime(1988, 12, 19)
        old_status = self._create_status_with_id_and_datetime(1, 
                                                              old_created_at)
        new_created_at = datetime.now()
        new_status = self._create_status_with_id_and_datetime(2, 
                                                              new_created_at)
        self.timeline.add_statuses([old_status, new_status])
        # get newers than `old_status`
        newers = self.timeline.get_newer_than(old_created_at)
        self.assertEqual(len(newers), 1)
        self.assertEqual(newers[0].id, new_status.id)
        # get newers than `new_status`
        newers = self.timeline.get_newer_than(new_created_at)
        self.assertEqual(len(newers), 0)

    def test_clear(self):
        old_created_at = datetime(1988, 12, 19)
        old_status = self._create_status_with_id_and_datetime(1, 
                                                              old_created_at)
        new_created_at = datetime.now()
        new_status = self._create_status_with_id_and_datetime(2, 
                                                              new_created_at)
        self.timeline.add_statuses([old_status, new_status])
        self.timeline.clear()
        self.assertEqual(len(self.timeline), 0)
        # add them again and check that they are inserted back
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(len(self.timeline), 2)

    def test_update_with_no_args(self):
        mock = MagicMock(name='update')
        timeline = Timeline([], mock)
        timeline.update()
        mock.assert_called_once_with()

    def test_update_with_one_arg(self):
        mock = MagicMock(name='update')
        arg = '#python'
        timeline = Timeline([], mock, arg)
        timeline.update()
        mock.assert_called_once_with(arg)

    def test_update_with_multiple_args(self):
        mock = MagicMock(name='update')
        args = ('#python', '#mock')
        timeline = Timeline([], mock, args)
        timeline.update()
        mock.assert_called_once_with(args)


class NamedTimelineListTest(unittest.TestCase):
    def setUp(self):
        self.named_timeline_list = NamedTimelineList()

    def test_has_timelines_false_if_empty(self):
        self.failIf(self.named_timeline_list.has_timelines())

    def test_has_timelines_true_otherwise(self):
        self.named_timeline_list.append_timeline('Timeline', [])
        self.failUnless(self.named_timeline_list.has_timelines())

    def test_active_index_minus_1_with_no_timelines(self):
        self.assertEqual(self.named_timeline_list.active_index, -1)

    def test_active_index_0_when_appending_first_timeline(self):
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        self.assertEqual(self.named_timeline_list.active_index, 0)

    def test_activate_previous(self):
        # -1 when there are no timelines
        self.named_timeline_list.activate_previous()
        self.assertEqual(self.named_timeline_list.active_index, -1)
        # does not change if its the first
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        self.assertEqual(self.named_timeline_list.active_index, 0)

    def test_activate_next(self):
        # -1 when there are no timelines
        self.named_timeline_list.activate_next()
        self.assertEqual(self.named_timeline_list.active_index, -1)
        # does not change if its the first
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        self.assertEqual(self.named_timeline_list.active_index, 0)

    def append_timeline(self):
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)

    def test_activate_previous_and_activate_next(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        # next
        self.named_timeline_list.activate_next()
        self.assertEqual(self.named_timeline_list.active_index, 1)
        self.named_timeline_list.activate_next()
        self.assertEqual(self.named_timeline_list.active_index, 2)
        # previous
        self.named_timeline_list.activate_previous()
        self.assertEqual(self.named_timeline_list.active_index, 1)
        self.named_timeline_list.activate_previous()
        self.assertEqual(self.named_timeline_list.active_index, 0)

    def test_get_active_timeline_name_returns_first_appended(self):
        # append
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        # assert
        active_timeline_name = self.named_timeline_list.get_active_timeline_name()
        self.assertEqual(name, active_timeline_name)

    def test_get_active_timeline_name_raises_exception_when_empty(self):
        self.assertRaises(Exception, self.named_timeline_list.get_active_timeline_name)

    def test_get_active_timeline_returns_first_appended(self):
        # append
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        # assert
        active_timeline = self.named_timeline_list.get_active_timeline()
        self.assertEqual(timeline, active_timeline)

    def test_get_active_timeline_raises_exception_when_empty(self):
        self.assertRaises(Exception, self.named_timeline_list.get_active_timeline)

    def test_append_timeline_increases_timeline_size(self):
        self.assertEqual(len(self.named_timeline_list), 0)
        name = 'Timeline'
        timeline = Timeline()
        self.named_timeline_list.append_timeline(name, timeline)
        self.assertEqual(len(self.named_timeline_list), 1)
        self.named_timeline_list.append_timeline(name, timeline)
        self.assertEqual(len(self.named_timeline_list), 2)

    # TODO test update functions with mocks
    # TODO get_*


if __name__ == '__main__':
    unittest.main()
