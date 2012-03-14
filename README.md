turses
======

A Twitter client with a curses interface written in Python. Most of the codebase 
is from the [Tyrs](http://tyrs.nicosphere.net) project by [Nicolas Paris](http://github.com/Nic0).

The goal of the project is to build a full-featured Twitter client that allows the
users to:
 * fully customize the client;
 * multiple UIs (`curses`, `gtk`, `qt`, et al.);
 * choose API backend (currently is using `python-twitter`); and 
 * implements all the capabilities of the Twitter API.

Features
========

 * Sexy curses interface
 * Multiple timelines (buffers)
 * Tweet, Reply, Retweet, Delete tweet
 * Follow/Unfollow
 * Favorite/Unfavorite
 * Search
 * Fully customizable
 * Pluggable UI

Roadmap
=======

 * Pluggable API
 * Documentation
 * DM
 * Thread view
 * User info
 * Lists
 * Multiple accounts
 * Geo
 * Blocking
 * Settings

Development
===========

`turses` is still a work in progress, a list of tasks can be found on 
the `TODO` file. 

Eventually every task will reside in the repository's [issue tracker](http://github.com/alejandrogomez/turses/issues). Feel free open issues with bugs, enhancements and features you will like
to see in `turses`; or hack them yourselves and send a pull request!

Code
====

The code is hosted on [GitHub](http://github.com/alejandrogomez/turses).

License
=======

`turses` is licensed under a GPLv3 license, see `LICENSE.txt` for the full text.
