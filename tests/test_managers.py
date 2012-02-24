###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('../')
import unittest

from mock import MagicMock

from turses.timeline import Timeline
from turses.managers import TimelineManager

class TimelineManagerTest(unittest.TestCase):
    def setUp(self):
        self.timeline = Timeline()

    def test_update_with_no_args(self):
        mock = MagicMock(name='update')
        self.timeline_manager = TimelineManager(self.timeline, mock)
        self.timeline_manager.update()
        mock.assert_called_once_with()

    def test_update_with_one_arg(self):
        mock = MagicMock(name='update')
        args = '#python'
        self.timeline_manager = TimelineManager(self.timeline, mock, args)
        self.timeline_manager.update()
        mock.assert_called_once_with(args)

    def test_update_with_multiple_args(self):
        mock = MagicMock(name='update')
        args = ('#python', '#mock')
        self.timeline_manager = TimelineManager(self.timeline, mock, args)
        self.timeline_manager.update()
        mock.assert_called_once_with(args)
        

if __name__ == '__main__':
    unittest.main()
