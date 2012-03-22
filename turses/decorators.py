###############################################################################
#                               coding=utf-8                                  #
#            Copyright (c) 2012 turses contributors. See AUTHORS.             #
#         Licensed under the GPL License. See LICENSE for full details.       #
###############################################################################

from functools import wraps
from threading import Thread


def wrap_exceptions(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
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
    """
    @wraps(func)
    def wrapper(self=None, *args, **kwargs):
        args = args, kwargs
        thread = Thread(target=func,
                        args=args)
        thread.run()

    return wrap_exceptions(wrapper)
