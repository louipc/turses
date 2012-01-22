###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('../')
import unittest

from credentials import *
from turses.api import Api
from turses.util import get_time
from turses.timeline import Timeline, TimelineException

        
class TimelineTest(unittest.TestCase):
    def setUp(self):
        self.api = Api(consumer_key, 
                       consumer_secret, 
                       access_token_key, 
                       access_token_secret)
        self.user = self.api.VerifyCredentials()
        self.timeline = Timeline(update_function=self.api.GetUserTimeline)

    def test_user_screen_name(self):
        self.assertEqual(self.user.screen_name, "tuitclient")

    def test_update_timeline(self):
        self.timeline.update_timeline()
        self.assertTrue(self.timeline.statuses)

    def test_updates_only_new_statuses(self):
        status_count = len(self.timeline)
        # post a new update
        #FIXME! TwitterError: Status is a duplicate
        self.api.PostUpdate(status="unittest at %s" % get_time())
        self.timeline.update_timeline()
        # check if we have one more status
        self.assertTrue(status_count == len(self.timeline) - 1)

    def test_raises_exception_without_update_function(self):
        self.timeline = Timeline()
        self.assertRaises(TimelineException, self.timeline.update_timeline)


if __name__ == '__main__':
    unittest.main()
