turses
======

A Twitter client for the console
--------------------------------

A ``turses`` session with multiple columns running on ``urxvt``:

.. image:: http://dialelo.com/img/turses_screenshot.png

The goal of the project is to build a full-featured, lightweight, and extremely 
configurable Twitter client.

Documentation
-------------

The documentation for ``turses`` is `available on ReadTheDocs
<http://turses.readthedocs.org>`_.

Take a look at `this screencast
<http://www.youtube.com/watch?v=kmnEdldw7WY>`_ for an
overview of the features of ``turses`` and its usage.

Installation
------------

If you downloaded the source code ::

    $ python setup.py install

With ``pip`` ::

    $ pip install turses

or (but `consider using pip`_):  ::

    $ easy_install turses

.. _`consider using pip`: http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install

Features
--------

- Multiple timelines (buffers)
- Multi-column
- Tweet, Reply, Retweet, Delete tweet
- Follow/Unfollow
- Favorite/Unfavorite
- Direct Messages
- Open URLs in browser
- Thread view
- Unread count
- Search
- View any user's tweets
- Fully customizable
- Multiple accounts

Development
-----------

The code is hosted on a `git repo`_.

.. _`git repo`: http://github.com/alejandrogomez/turses

``turses`` is evolving fast, a list of tasks can be found on 
the on the `issue tracker`_. Feel free to submit issues, feature
requests or participate in ongoing discussions.

.. _`issue tracker`: http://github.com/alejandrogomez/turses/issues

If you feel hackish, reading the `dev docs`_ is recommended.

.. _`dev docs`: http://turses.readthedocs.org/en/latest/dev/internals.html

To contribute code:
 1. Create a branch from ``develop``
 2. Code following `pep8 rules`_.
 3. Commit your changes
 4. Add yourself to ``AUTHORS``
 5. Send a pull request to the ``develop`` branch

.. _`pep8 rules`: http://www.python.org/dev/peps/pep-0008

Any feedback is very much appreciated.

Roadmap
-------

- Lists
- Streaming
- Notifications
- Sessions

License
-------

``turses`` is licensed under a GPLv3 license, see ``LICENSE`` for details.

Authors
-------

``turses`` is based on `Tyrs`_ by `Nicolas Paris`_.

.. _`Tyrs`: http://tyrs.nicosphere.net
.. _`Nicolas Paris`: http://github.com/Nic0

See ``AUTHORS`` for a full list of contributors.
