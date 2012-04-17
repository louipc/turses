0.1.1
-----
- bindings to update all timelines
- bugfix: `generate_token_file` instead of `create_token_file`

0.1.0
-----
- binding to open focused status authors' tweets
- reload configuration
- configuration default location and format changed

0.0.15
------
- bugfix: DM recipient was not correctly resolved
- fetch newer tweets when scrolling up from the top and viceversa
- show retweets by default

0.0.14
------
- bugfix: logging

0.0.13
------
- thread view

0.0.12
------
- multiple visible timelines in columns
- fix bug with unicode input
- open URLs in browser

0.0.11
------
- include retweets in home timeline
- fix bug with non-existent method

0.0.10
------
- unread count
- mark all tweets in active timeline as read
- fix (again) a bug with mouse events

0.0.9
-----
- compose tweet with same hashtags as the focused status
- create search timeline with hashtags from focused status

0.0.8
-----
- fix bug: self follow/unfollow
- fix bug: editor signals
- direct messages :)
- persistent timeline cursor

0.0.7
-----
- fix critical bug, missing dependency urwid

0.0.6
-----
- fix bug with mouse events
- relative imports to avoid `ImportError` exceptions

0.0.5
-----
- more colorful defaults
- see your own tweets
- search for a user's tweets

0.0.4
-----
- follow and unfollow
- pluggable UI and API
- associate callbacks to API calls

0.0.3
-----
- bug with non-ascii characters in search solved
- asynchronous API calls
- favorite/unfavorite tweets
- Favorites timeline

0.0.2
-----
- tests with coverage check
- fixed bug with missing dependency in `setup.py`
- decoration for tabs
