# -*- coding: utf-8 -*-

"""
turses.meta
~~~~~~~~~~~

This module contains abstract classes and decorators.
"""

from abc import ABCMeta, abstractmethod, abstractproperty
from functools import wraps
from threading import Thread

# - Decorators ----------------------------------------------------------------

def wrap_exceptions(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments.

    Executes the decorated function in a try except block and calls
    `on_success` (if given) if no exception was raised, otherwise calls
    `on_error` (if given).
    """
    @wraps(func)
    def wrapper(self=None, *args, **kwargs):
        on_error = kwargs.pop('on_error', None)
        on_success = kwargs.pop('on_success', None)

        try:
            result = func(self, *args, **kwargs)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()
            return result

    return wrapper


def async(func):
    """
    Decorator for executing a function asynchronously.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper

# - Abstract classes ----------------------------------------------------------

class ActiveList(object):
    """
    A list that contains an 'active' element.

    This abstract class implements some functions but the subclasses must
    define `active` property, as well as `is_valid_index` and `activate_last`
    methods.
    """
    __metaclass__ = ABCMeta

    NULL_INDEX = -1

    def __init__(self):
        self.active_index = self.NULL_INDEX

    @abstractproperty
    def active(self):
        pass

    @abstractmethod
    def is_valid_index(self, index):
        pass

    def activate_previous(self):
        """Mark as active the previous element if it exists."""
        new_index = self.active_index - 1
        if self.is_valid_index(new_index):
            self.active_index = new_index

    def activate_next(self):
        """Mark as active the next element if it exists."""
        new_index = self.active_index + 1
        if self.is_valid_index(new_index):
            self.active_index = new_index

    def activate_first(self):
        """Mark the first element as the 'active' if it exists."""
        first = 0
        if self.is_valid_index(first):
            self.active_index = first
        else:
            self.active_index = self.NULL_INDEX

    @abstractmethod
    def activate_last(self):
        pass


class UnsortedActiveList(ActiveList):
    """
    An `ActiveList` in which the 'active' element can be shifted position by
    position, to the begging and to the end.

    All the methods that this class contains are abstract.
    """

    @abstractmethod
    def shift_active_previous(self):
        """Shift the active element one position to the left."""
        pass

    @abstractmethod
    def shift_active_next(self):
        """Shift the active element one position to the right."""
        pass

    @abstractmethod
    def shift_active_beggining(self):
        """
        Shift the active element (if any) to the begginning of the list.
        """
        pass

    @abstractmethod
    def shift_active_end(self):
        """
        Shift the active element (if any) to the begginning of the list.
        """
        pass


class Updatable:
    """
    An abstract class that for making a class 'updatable'.
    """

    __metaclass__ = ABCMeta

    def __init__(self,
                 update_function=None,
                 update_function_args=None,
                 update_function_kwargs=None,):
        """
        `update_function` is the function used to update the class, with
        the args `update_function_args` and `update_function_kwargs` if
        they are provided.
        """
        self.update_function = update_function

        if isinstance(update_function_args, tuple):
            self._args = list(update_function_args)
        elif update_function_args:
            self._args = [update_function_args]
        else:
            self._args = []

        if update_function_kwargs:
            self._kwargs = dict(update_function_kwargs)
        else:
            self._kwargs = {}

    @wrap_exceptions
    def update(self, **extra_kwargs):
        """
        Update the object, after receiving the result it is passed to the 
        `update_callback` function.
        """
        if not self.update_function:
            return

        args = self._args
        kwargs = self._kwargs
        kwargs.update(extra_kwargs)

        result = self.update_function(*args, **kwargs)

        self.update_callback(result)

    @abstractmethod
    def update_callback(self, result):
        pass


