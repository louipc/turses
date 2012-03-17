###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

from functools import wraps, partial


def wrap_exceptions(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
    """
    @wraps(func)
    def wrapper(self=None, on_error=None, on_success=None, **kwargs):
        try:
            result = func(self, **kwargs)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()
            return result

    return wrapper

def wrap_exceptions_args(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except:
            on_error = kwargs.get('on_error')
            if callable(on_error):
                on_error()
        else:
            on_success = kwargs.get('on_success')
            if callable(on_success):
                on_success()
            return result

    return partial(wrapper, on_error=None, on_success=None)
