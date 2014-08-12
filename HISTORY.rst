0.2.23
------
- Upgrade Tweepy dependency to 2.3

0.2.22
------
- Upgrade Tweepy dependency to 2.2

0.2.21
------
- Bugfix: Turses no longer crashes when clicking on the window

0.2.20
------
- Mouse scrolling support (thanks to Wes Turner)
- Bugfix: Escape HTML entities without borking tweet text (thanks to David Tiersch)

0.2.19
------
- Bugfix: Restore Python 2.6 compatibility

0.2.18
------
- Bugfix: use ASCII characters for reply and retweet indicators

0.2.17
------
- Make Ctrl-C act as escape
- Hashtag searches in sessions

0.2.16
------
- Update to tweepy 2.1, fix search functionality

0.2.15
------
- Configurable retweet and reply indicators

0.2.14
------
- Daemonize threads so they finish when quitting turses
- Fix a bug regarding SIGCONT handling

0.2.13
------
- `Y` as shortcut for retweeting and favoriting a tweet

0.2.12
------
- Upgrade to Tweepy 2.0 (hence Twitter API v1.1)

0.2.11
------
- Include ``in_reply_to_status_id`` parameter in replies

0.2.10
------
- Use HTTPS by default (thanks to Joe Di Castro)

0.2.9
-----
- Configurable number of statuses in user info widget
- Sessions support
- Better information for SSL errors

0.2.8
-----
- Python 2.6 support

0.2.7
-----
- center focus when receiving tweets after scrolling down the bottom
- get your tweets that have been retweeted

0.2.6
-----
- configurable URL format
- better browser integration (by Paul Ivanov)

0.2.5
-----
- search commands also available with no timelines
- clear the status bar in every mode
- asynchronous search timeline addition
- keep columns when deleting a buffer within them
- bugfix: crashed when deleting all buffers

0.2.4
-----
- bugfix: unable to focus the topmost status when having multiple columns

0.2.3
-----
- per-account configuration
- bugfix: crashed when navigating to empty buffers

0.2.2
-----
- fix regression: timelines not updating periodically

0.2.1
-----
- bugfix: the Twitter entities were not processed every time

0.2.0
-----
- logging

0.1.18
------
- bugfix: crash when rendering direct messages

0.1.17
------
- `developer docs`_
- border around editor
- bugfix: help and version were removed by stdout replacement
- debug mode
- offline debugging

.. _`developer docs`: http://turses.readthedocs.org/en/latest/dev/internals.html

0.1.16
------
- show a popup with user info when pressing `i`

0.1.15
------
- configurable editor alignment
- make `turses` play nicely with terminal multiplexers (Joe Di Castro)
- follow and unfollow users typing their nick in an editor (Giannis Damigos)
- bugfix: pressing <Esc> in search user editor made `turses` crash
- bugfix: avoid duplicate usernames in replies

0.1.14
------
- bugfix: crash when shifting buffers to the beginning or end

0.1.13
------
- bugfix: could not remove own retweets
- bugfix: inconsistencies with help

0.1.12
------
- bugfix: missing key binding in help (Giannis Damigos)
- bugfix: status messages cleared the editor
- configurable status bar visibility
- changes to manual retweet template
- set console title to turses
- `docs on readthedocs <http://readthedocs.org/docs/turses/en/latest/>`_

0.1.11
------
- bugfix: exception when marking tweet as favorite

0.1.10
------
- expanded URLs for search results
- bugfix: crashed when expanded URLs were missing

0.1.9
-----
- open focused status in a browser
- show expanded URLs

0.1.8
-----
- bugfix: packaging error

0.1.7
-----
- bugfix: inconsistencies when navigating tweets with arrow keys
- configurable status wrappers: box, divider or none

0.1.6
-----
- colored urls
- colored favorites
- bugfix: non-ascii characters on templates made `turses` crash
- visual indicators for status types (retweet, reply, favorite)

0.1.5
-----
- configurable tab text
- colored hashtags and usernames

0.1.4
-----
- update all timelines periodically
- configurable default timelines
- bugfix: don't crash with empty timelines
- bugfix: manual retweet crashed
- bugfix: don't capture all input

0.1.3
-----
- bugfix: packaging error

0.1.2
-----
- bugfix: error with packaging

0.1.1
-----
- bindings to update all timelines
- bugfix: `generate_token_file` instead of `create_token_file`

0.1.0
-----
- binding to open focused status authors' tweets
- reload configuration
- configuration default location and format changed
