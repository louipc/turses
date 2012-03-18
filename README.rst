turses: a Twitter client written in Python
==========================================

A Twitter client with a curses interface written in Python. Various parts of the codebase 
are borrowed from the `Tyrs`_ project by `Nicolas Paris`_.

.. _`Tyrs`: http://tyrs.nicosphere.net
.. _`Nicolas Paris`: http://github.com/Nic0

The goal of the project is to build a full-featured Twitter client:

- one that is fully  customizable;
- usable with multiple UIs (curses, gtk, qt, etc.); 
- plugged to different API backends (currently is using `python-twitter`_); and 
- having all the Twitter API capabilities with some spice.

.. _`python-twitter`: http://code.google.com/p/python-twitter/

Installation
------------

**turses** is installed simply by:  ::

    $ pip install turses

or (but you should consider using pip):  ::

    $ easy_install turses

Features
--------

- Sexy curses interface
- Multiple timelines (buffers)
- Tweet, Reply, Retweet, Delete tweet
- Follow/Unfollow
- Favorite/Unfavorite
- Search
- View any user's tweets
- Fully customizable
- Pluggable UI
- Pluggable API
- Multiple accounts

Roadmap
-------

- Documentation
- DM
- Thread view
- Lists
- Geo
- Blocking
- Improve settings

Development
-----------

**turses** is still a work in progress, a list of tasks can be found on 
the TODO file. Eventually every task will reside in the repository's 
`issue tracker`_. 

.. _`issue tracker`: http://github.com/alejandrogomez/turses/issues

Feel free to open issues with bugs, enhancements and features you will like
to see in **turses**; or hack them yourselves and send a pull request!

Code
----

The code is hosted on `GitHub`_.

.. _`GitHub`: http://github.com/alejandrogomez/turses

Screenshots
-----------

.. image:: http://dialelo.com/img/turses_buffers.png

License
-------

**turses** is licensed under a GPLv3 license, see LICENSE for details.
