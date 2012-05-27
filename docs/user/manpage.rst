===============
 turses
===============

---------------------------------------------
a Twitter client with a sexy curses interface
---------------------------------------------

:Date:   2012-05-19
:Version: 0.1.4
:Manual section: 1
:Manual group: User Commands


``turses`` is a Twitter client for the console.

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


Setup
-----

The standard location is under `$HOME` directory, in a folder called `.turses`. There is some configurations file in turses:
::

 -config: contains user preferences: colors, bindings, etc.
 -token: contains authentication token for the default user account

Each user account that is no the default one has its .token file. After inserting the PIN code, a new .token file will appear in your configuration directory

Now, when you execute turses, you will be logged in with the previously stored credentials.

Motion
------

 - up (k) - scroll up.
 - down (j) - scroll down
 - left (h) -  activate the timeline on the left
 - right (l) - activate the timeline on the right
 - scroll_to_top (g) - scroll to top
 - scroll_to_bottom (G) -  scroll to bottom

Tweets
------
- tweet (t) - compose a tweet
- delete_tweet (X) - delete focused status
- reply (r) - reply to focused status
- retweet (R) - retweet focused status
- retweet_and_edit (E) - open a editor for manually retweeting the focused status status
- send_dm (D) - compose a direct message
- update (u) - refresh the active timeline
- update_all (S) - refresh all the timelines
- tweet_hashtag (H) - compose a tweet with the same hashtags as the focused status
- fav (b) - mark focused tweet as favorite
- delete_fav (ctrl b) - remove tweet from favorites
- follow_selected (f) - follow selected status author
- unfollow_selected (U) - unfollow selected status author

Buffers
-------
- activate_first_buffer (a) - activate first buffer
- activate_last_buffer (e) - activate last buffer
- shift_buffer_beggining (ctrl a shift) - active buffer to the beginning
- shift_buffer_end (ctrl e shift) - active buffer to the end
- shift_buffer_left (< shift)  - active buffer one position to the left
- shift_buffer_right (> shift) - active buffer one position to the right
- expand_visible_left (p) - expand visible timelines one column to the left
- expand_visible_right (n) - expand visible timelines one column to the right
- shrink_visible_left (P) - shrink visible timelines one column from the left
- shrink_visible_right (N) - shrink visible timelines one column from the left
- delete_buffer (d) - delete buffer
- clear (c) - clear status bar
- mark_all_as_read (A) - mark all tweets in the current timeline as read

Timelines
---------

- home (.) - open a home timeline
- own_tweets (_) - open a timeline with your tweets
- favorites (B) - open a timeline with your favorites
- mentions (m) - open a mentions timeline
- DMs (M) - open a direct message timeline
- search (/) - search for term and show resulting timeline
- search_user (@) - open a timeline with the tweets of the specified user
- user_timeline (+) - open a timeline with the tweets of the focused status author
- thread (T) - open the thread of the focused status
- hashtags (L) - open a search timeline with the hashtags of the focused status

Meta
----

- help (?) - show program help
- reload_config (C) - reload configuration


Other commands
--------------

- quit (q) -  exit program
- openurl (o) - open URLs of the focused status in a browser
- redraw (ctrl l) -  redraw the screen

Author
------

``turses`` was written by Alejandro Gomez <alejandroogomez@gmail.com>

This manual page was written by Daniel Echeverry for the Debian GNU/Linux system
(but may be used by others).

