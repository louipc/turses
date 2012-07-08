# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.ui import StatusWidget
from tests  import create_status, create_direct_message


class StatusWidgetTest(unittest.TestCase):
    def test_create_with_status(self):
        # load the defaults
        status = create_status()
        StatusWidget(status)

    def test_create_with_direct_message(self):
        # load the defaults
        direct_message = create_direct_message()
        StatusWidget(direct_message)



if __name__ == '__main__':
    unittest.main()
