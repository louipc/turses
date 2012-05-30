# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.config import Configuration
from turses.ui import StatusWidget
from tests  import create_status, create_direct_message


class StatusWidgetTest(unittest.TestCase):
    def test_create_with_status(self):
        # load the defaults
        configuration = Configuration()
        status = create_status()
        StatusWidget(status, configuration)

    def test_create_with_direct_message(self):
        # load the defaults
        configuration = Configuration()
        direct_message = create_direct_message()
        StatusWidget(direct_message, configuration)



if __name__ == '__main__':
    unittest.main()
