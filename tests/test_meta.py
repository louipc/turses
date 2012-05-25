# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.meta import ActiveList


class ActiveListTest(unittest.TestCase):
    """
    A helper class for testing subclasses of the `turses.meta.ActiveList`
    abstract class.
    """
    def assert_null_index(self):
        """Assert that the `active_index` in `self.timeline` is
        `turses.meta.ActiveList.NULL_INDEX`"""
        self.assertEqual(self.active_index(),
                         ActiveList.NULL_INDEX)

    def active_index(self):
        raise NotImplementedError


if __name__ == '__main__':
    unittest.main()
