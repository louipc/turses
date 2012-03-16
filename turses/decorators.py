###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


# TODO do this with introspection

def wrap_exceptions(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
    """
    def wrapper(self, on_error=None, on_success=None):
        try:
            func(self)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def wrap_exceptions_arg(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
    """
    def wrapper(self, arg, on_error=None, on_success=None):
        try:
            func(self, arg)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def wrap_exceptions_args(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Executes the decorated function in a try except block and calls `on_success` 
    (if given) if no exception was raised, otherwise calls `on_error` (if given).
    """
    def wrapper(self, an_arg, another_arg, on_error=None, on_success=None):
        try:
            func(self, an_arg, another_arg)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def wrap_exceptions_returns(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Returns the result of executing the decorated function inside a try except 
    block. Calls `on_success` (if given) if no exception was raised, otherwise 
    calls `on_error` (if given).
    """
    def wrapper(self, on_error=None, on_success=None):
        try:
            result = func(self)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()
            return result

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper

def wrap_exceptions_returns_arg(func):
    """
    Augments the function arguments with the `on_error` and `on_success`
    keyword arguments. 
    
    Returns the result of executing the decorated function inside a try except 
    block. Calls `on_success` (if given) if no exception was raised, otherwise 
    calls `on_error` (if given).
    """
    def wrapper(self, arg, on_error=None, on_success=None):
        try:
            result = func(self, arg)
        except:
            if callable(on_error):
                on_error()
        else:
            if callable(on_success):
                on_success()
            return result

    wrapper.__name__ = func.__name__
    wrapper.__module__ = func.__module__
    wrapper.__dict__ = func.__dict__
    wrapper.__doc__ = func.__doc__
    return wrapper
