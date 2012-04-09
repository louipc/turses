###############################################################################
#                               coding=utf-8                                  #
#            Copyright (c) 2012 turses contributors. See AUTHORS.             #
#         Licensed under the GPL License. See LICENSE for full details.       #
###############################################################################

import sys
sys.path.append('../')
import unittest
from datetime import datetime

from mock import MagicMock

from turses.models import Status, Timeline, TimelineList, ActiveList


# TODO
class HelperFunctionTest(unittest.TestCase):
    pass


# TODO
class StatusTest(unittest.TestCase):
    pass


# TODO
class UserTest(unittest.TestCase):
    pass


# TODO
class DirectMessageTest(unittest.TestCase):
    pass


# TODO
class ListTest(unittest.TestCase):
    pass


# TODO
class UnsortedActiveListTest(unittest.TestCase):
    pass


class TimelineTest(unittest.TestCase):
    def setUp(self):
        self.timeline = Timeline()
        self.timeline.clear()
        self.assertEqual(len(self.timeline), 0)
        self.assertEqual(self.timeline.active_index, -1)

    def _create_status(self, id, datetime):
        from calendar import timegm
        created_at_in_seconds = timegm(datetime.utctimetuple())
        return Status(id=id,
                      created_at_in_seconds=created_at_in_seconds,
                      user='test',
                      text='Test',)

    def test_unique_statuses_in_timeline(self):
        self.assertEqual(len(self.timeline), 0)
        # create and add the status
        status = self._create_status(1, datetime.now())
        self.timeline.add_status(status)
        self.assertEqual(len(self.timeline), 1)
        # check that adding more than once does not duplicate element
        self.timeline.add_status(status)
        self.assertEqual(len(self.timeline), 1)

    def test_active_index_becomes_0_when_adding_first_status(self):
        status = self._create_status(1, datetime.now())
        self.timeline.add_status(status)
        self.assertEqual(self.timeline.active_index, 0)
        # check that adding than once does not move the active
        self.timeline.add_status(status)
        self.assertEqual(self.timeline.active_index, 0)

    def test_insert_different_statuses(self):
        old_status = self._create_status(1, datetime(1988, 12, 19))
        new_status = self._create_status(2, datetime.now())
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(len(self.timeline), 2)

    def test_insert_different_statuses_individually(self):
        old_status = self._create_status(1, datetime(1988, 12, 19))
        new_status = self._create_status(2, datetime.now())
        self.timeline.add_status(old_status)
        self.assertEqual(len(self.timeline), 1)
        self.timeline.add_status(new_status)
        self.assertEqual(len(self.timeline), 2)

    def test_statuses_ordered_reversely_by_date(self):
        old_status = self._create_status(1, datetime(1988, 12, 19))
        new_status = self._create_status(2, datetime.now())
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(self.timeline[0], new_status)
        self.assertEqual(self.timeline[1], old_status)

    def test_get_newer_than(self):
        old_created_at = datetime(1988, 12, 19)
        old_status = self._create_status(1, old_created_at)
        new_created_at = datetime.now()
        new_status = self._create_status(2, new_created_at)
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
        old_status = self._create_status(1, old_created_at)
        new_created_at = datetime.now()
        new_status = self._create_status(2, new_created_at)
        self.timeline.add_statuses([old_status, new_status])
        self.timeline.clear()
        self.assertEqual(len(self.timeline), 0)
        # add them again and check that they are inserted back
        self.timeline.add_statuses([old_status, new_status])
        self.assertEqual(len(self.timeline), 2)

    def test_update_with_no_args(self):
        mock = MagicMock(name='update')
        timeline = Timeline(update_function=mock,)
        timeline.update()
        mock.assert_called_once_with()

    def test_update_with_one_arg(self):
        mock = MagicMock(name='update')
        arg = '#python'
        timeline = Timeline(update_function=mock, update_function_args=arg)
        timeline.update()
        mock.assert_called_once_with(arg)

    def test_update_with_multiple_args(self):
        mock = MagicMock(name='update')
        args = ('#python', '#mock')
        timeline = Timeline(update_function=mock, update_function_args=args)
        timeline.update()
        mock.assert_called_once_with(args)

    def test_update_with_kargs(self):
        mock = MagicMock(name='update')
        args = ({'text': '#python', 'action': 'search'})
        timeline = Timeline(update_function=mock, update_function_args=args)
        timeline.update()
        mock.assert_called_once_with(args)

    def test_update_with_args_and_kargs(self):
        mock = MagicMock(name='update')
        args = ('twitter', 42, {'text': '#python', 'action': 'search'})
        timeline = Timeline(update_function=mock, update_function_args=args)
        timeline.update()
        mock.assert_called_once_with(args)


class TimelineListTest(unittest.TestCase):
    def setUp(self):
        self.timeline_list = TimelineList()

    def test_has_timelines_false_if_empty(self):
        self.failIf(self.timeline_list.has_timelines())

    def append_timeline(self):
        self.timeline_list.append_timeline(Timeline('Timeline'))

    def test_has_timelines_true_otherwise(self):
        self.append_timeline()
        self.failUnless(self.timeline_list.has_timelines())

    def test_active_index_minus_1_with_no_timelines(self):
        self.assertEqual(self.timeline_list.active_index, -1)

    def test_active_index_0_when_appending_first_timeline(self):
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_previous(self):
        # -1 when there are no timelines
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the first
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_next(self):
        # -1 when there are no timelines
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the last
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_previous_and_activate_next(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        # next
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 2)
        # previous
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_get_active_timeline_name_returns_first_appended(self):
        # append
        name = 'Timeline'
        timeline = Timeline(name)
        self.timeline_list.append_timeline(timeline)
        # assert
        active_timeline_name = self.timeline_list.get_active_timeline_name()
        self.assertEqual(name, active_timeline_name)

    def test_get_active_timeline_name_raises_exception_when_empty(self):
        self.assertRaises(Exception, self.timeline_list.get_active_timeline_name)

    def test_get_active_timeline_returns_first_appended(self):
        # append
        name = 'Timeline'
        timeline = Timeline(name)
        self.timeline_list.append_timeline(timeline)
        # assert
        active_timeline = self.timeline_list.get_active_timeline()
        self.assertEqual(timeline, active_timeline)

    def test_get_active_timeline_raises_exception_when_empty(self):
        self.assertRaises(Exception, self.timeline_list.get_active_timeline)

    def test_append_timeline_increases_timeline_size(self):
        self.assertEqual(len(self.timeline_list), 0)
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 1)
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 2)

    def test_activate_first(self):
        # -1 when there are no timelines
        self.timeline_list.activate_first()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the first
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_first()
        self.assertEqual(self.timeline_list.active_index, 0)
        # moves to the first when in another position
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.activate_next()
        self.timeline_list.activate_next()
        self.timeline_list.activate_first()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_last(self):
        # -1 when there are no timelines
        self.timeline_list.activate_last()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the last
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_last()
        self.assertEqual(self.timeline_list.active_index, 0)
        # moves to the last when in another position
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.activate_last()
        self.assertEqual(self.timeline_list.active_index, 2)

    def test_shift_active_previous(self):
        # -1 when there are no timelines
        self.timeline_list.shift_active_previous()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the first
        self.append_timeline()
        self.timeline_list.shift_active_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_shift_active_next(self):
        # -1 when there are no timelines
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, -1)
        # does not change if its the last
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 0)
        # it increases until reaching the end
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 2)
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 2)

    # TODO get_*


if __name__ == '__main__':
    unittest.main()
