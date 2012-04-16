turses: a Twitter client featuring a curses interface
=====================================================

``turses`` is a Twitter client with a sexy curses interface written in Python. Various 
parts of the codebase are borrowed from the `Tyrs`_ project by `Nicolas Paris`_.

.. _`Tyrs`: http://tyrs.nicosphere.net
.. _`Nicolas Paris`: http://github.com/Nic0

The goal of the project is to build a full-featured and flexible Twitter client.

Installation
------------

If you downloaded the source code ::

    $ python setup.py install

With ``pip`` ::

    $ pip install turses

or (but `you should consider using pip <http://www.pip-installer.org/en/latest/other-tools.html#pip-compared-to-easy-install>`_):  ::

    $ easy_install turses

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
the TODO file. Eventually every task will reside in the repository's 
`issue tracker`_.  

.. _`issue tracker`: http://github.com/alejandrogomez/turses/issues

To contribute code:
 1. Create a branch from ``develop``
 2. Commit your changes
 3. Send a pull request

Any feedback is very much appreciated.

Roadmap
-------

- Documentation
- Lists
- Streaming
- Notifications
- Geo
- Blocking

Screenshots
-----------

A ``turses`` session with multiple columns running on ``urxvt``:

.. image:: http://dialelo.com/img/turses_buffers.png

License
-------

``turses`` is licensed under a GPLv3 license, see LICENSE for details.
