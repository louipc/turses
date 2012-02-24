###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('../')
import unittest

from turses.timeline import Timeline
from turses.managers import TimelineManager

class TimelineManagerTest(unittest.TestCase):
    def setUp(self):
        self.timeline = Timeline()
        self.TimelineManager(self.timeline, lambda x:[])

    # TODO
    #  mocks or stubs
        

if __name__ == '__main__':
    unittest.main()
