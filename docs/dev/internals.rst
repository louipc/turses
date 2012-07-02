Internals
=========

Overview
--------

Here is an overview of the multiple files that compound `turses`, each
of them with a comment explaining their goal.

.. code-block:: sh

    turses
    ├── requirements
    │   ├── base.txt
    │   └── dev.txt
    ├── setup.py
    └── turses
        ├── api
        │   ├── base.py      # definition of an interface to the Twitter API
        │   ├── backends.py  # Twitter API implementations
        │   ├── debug.py     # mock API implementation for debugging
        │   └── __init__.py
        ├── cli.py           # logic for launching `turses`
        ├── config.py        # configuration management
        ├── core.py          # core logic: controller and event handling
        ├── __init__.py
        ├── models.py        # data structures
        ├── ui.py            # UI widgets
        └── utils.py         # misc funcions that don't fit elsewhere

``turses.cli``
--------------

.. automodule:: turses.cli

.. autofunction:: turses.cli.main

``turses.config``
-----------------

.. autoclass:: turses.config.Configuration

``turses.core``
---------------

.. automodule:: turses.core

.. autoclass:: turses.core.KeyHandler
.. autoclass:: turses.core.Controller

``turses.meta``
---------------

.. automodule:: turses.meta

Decorators
~~~~~~~~~~

.. autofunction:: turses.meta.wrap_exceptions
.. autofunction:: turses.meta.async
.. autofunction:: turses.meta.filter_result

Abstract classes
~~~~~~~~~~~~~~~~

These abstract classes are meant to provide a very general pieces of
functionality:

.. autoclass:: turses.meta.ActiveList
.. autoclass:: turses.meta.UnsortedActiveList
.. autoclass:: turses.meta.Updatable

``turses.models``
-----------------

.. automodule:: turses.models

Base model
~~~~~~~~~~

The model on which ``turses`` is based is :attr:`~turses.models.TimelineList`,
a list of *updatable* :attr:`~turses.models.Timeline` objects.

.. autoclass:: turses.models.TimelineList

Twitter models
~~~~~~~~~~~~~~

The Twitter entities represented on ``turses`` are the following:

.. autoclass:: turses.models.Timeline
.. autoclass:: turses.models.User
.. autoclass:: turses.models.Status
.. autoclass:: turses.models.DirectMessage
.. autoclass:: turses.models.List

``turses.ui``
-------------

.. automodule:: turses.ui

:attr:`~turses.ui.CursesInterface` is the main UI widget, which provides a
generic API to draw the representation of the
:attr:`~turses.models.TimelineList`, help and an intro screen:

.. autoclass:: turses.ui.CursesInterface

.. note::

    The list of widgets presented here is not complete.

Interfaces
~~~~~~~~~~

The extraction of interfaces from the widgets is still in process. Here are
the ones that have been extracted:

.. autoclass:: turses.ui.Scrollable


Widget wrappers
~~~~~~~~~~~~~~~

``turses`` make heavy usage of the ``urwid.WidgetWrap`` class to compose custom
widgets. 

:attr:`~turses.ui.ScrollableWidgetWrap` helps to make widgets that 
implement the :attr:`~turses.ui.Scrollable` interface, thus are navigable with
the motion commands ``up``, ``down``, ``scroll_to_top`` and
``scroll_to_bottom``.

.. autoclass:: turses.ui.ScrollableWidgetWrap


Widgets
~~~~~~~

Here's a list with some of the widgets that represent Twitter entities:

.. autoclass:: turses.ui.TimelinesBuffer
.. autoclass:: turses.ui.StatusWidget
.. autoclass:: turses.ui.UserInfo

``turses.utils``
----------------

.. automodule:: turses.utils
