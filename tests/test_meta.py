# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from mock import Mock

from turses.meta import ActiveList, Observable, notify


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


class ObservableTest(unittest.TestCase):
    def setUp(self):
        self.observable = Observable()
        self.observer = Mock()
        self.observable.subscribe(self.observer)

    def test_notify_method_calls_update_on_observers(self):
        self.observable.notify()

        self.observer.update.assert_called_once()

    def test_methods_with_notify_decorator(self):
        # decorate `method`
        method = notify(lambda self: None)

        # pass `self.observable` as the first arguments to emulate a instance
        # method
        method(self.observable)

        self.observer.update.assert_called_once()

    def test_unsubscribe(self):
        self.observable.unsubscribe(self.observer)

        self.observable.notify()

        self.assertFalse(self.observer.update.called)



if __name__ == '__main__':
    unittest.main()
