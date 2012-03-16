turses: a Twitter client written in Python
==========================================

A Twitter client with a curses interface written in Python. Various parts of the codebase 
are borrowed from the `Tyrs`_ project by `Nicolas_Paris`_.

.. _`Tyrs`: http://tyrs.nicosphere.net
.. _`Nicolas_Pars`: http://github.com/Nic0

The goal of the project is to build a full-featured Twitter client that is:

- fully  customizable;
- usable within multiple UIs (*curses*, *gtk*, *qt*, et al.);
- plugged to different API backends (currently is using `python-twitter`); and 
- implementing all the Twitter API capabilities and adds some spice.

Instalation
-----------

**turses** is installed simply by: ::
    $ pip install turses

or: ::
    $ easy_install turses

Features
--------

- Sexy curses interface
- Multiple timelines (buffers)
- Tweet, Reply, Retweet, Delete tweet
- Follow/Unfollow
- Favorite/Unfavorite
- Search
- Fully customizable
- Pluggable UI
- Pluggable API

Roadmap
-------

- Documentation
- DM
- Thread view
- User info
- Lists
- Multiple accounts
- Geo
- Blocking
- Settings

Development
-----------

**turses** is still a work in progress, a list of tasks can be found on 
the `TODO`_ file. 

.. _`TODO`: http://github.com/alejandrogomez/turses/blob/master/TODO.rst

Eventually every task will reside in the repository's `issue tracker`_. 

.. _`issue tracker`: http://github.com/alejandrogomez/turses/issues

Feel free to open issues with bugs, enhancements and features you will like
to see in **turses**; or hack them yourselves and send a pull request!

Code
----

The code is hosted on `GitHub`_.

.. _`GitHub`: http://github.com/alejandrogomez/turses

License
-------

**turses** is licensed under a GPLv3 license, see LICENSE for details.
