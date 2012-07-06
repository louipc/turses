# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest
from datetime import datetime

from mock import MagicMock

from tests import create_status, create_direct_message
from tests.test_meta import ActiveListTest
from turses.models import (prepend_at, sanitize_username, parse_attributes,
                           is_DM, is_username, is_hashtag,

                           Timeline, TimelineList)


class HelperFunctionTest(unittest.TestCase):
    def test_is_DM(self):
        # status is NOT a DM
        status = create_status()
        self.failIf(is_DM(status))

        dm = create_direct_message()
        self.failUnless(is_DM(dm))

    def test_is_username(self):
        valid = ['dialelo', 'mental_floss', '4n_4Wfu1_US3RN4M3']
        for user in valid:
            self.failUnless(is_username(user))

        invalid = ['-asd', 'adsd?']

        for user in invalid:
            self.failIf(is_username(user))

    def test_is_hashtag(self):
        valid = ['#turses', '#cúrcuma', '#4n_4Wfu1_H45hT46']
        for hashtag in valid:
            self.failUnless(is_hashtag(hashtag))

        invalid = ['s#turses', '#']
        for hashtag in invalid:
            self.failIf(is_hashtag(hashtag))

    def test_sanitize_username(self):
        dirty_and_clean = [
            ('@dialelo',           'dialelo'),
            ('dialelo',            'dialelo'),
            ('?@mental_floss',     'mental_floss'),
            ('@4n_4Wfu1_US3RN4M3', '4n_4Wfu1_US3RN4M3'),
        ]
        for dirty, clean in dirty_and_clean:
            sanitized = sanitize_username(dirty)
            self.assertEqual(sanitized, clean)

    def test_parse_attributes(self):
        text = '@asdf http://www.dialelo.com #asf'

        expected_result = [('attag', u'@asdf'), u' ',
                           ('url', u'http://www.dialelo.com'), u' ',
                           ('hashtag', u'#asf')]

        result = parse_attributes(text=text,
                                  hashtag='hashtag',
                                  attag='attag',
                                  url='url')
        self.assertEqual(result, expected_result)

    def test_is_valid_status_text(self):
        pass

    def test_is_valid_search_text(self):
        pass


class StatusTest(unittest.TestCase):

    # map attributes

    def test_map_attributes_with_mentions_hashtags_and_url(self):
        text = (u'@aaloy  QT @Pybonacci: \xa1Qu\xe9 pasada con Vim!'
                u' #Python #IDE RT @dialelo uso un setup parecido a este: '
                u'http://t.co/5lTGNzba')
        entities = {
            u'user_mentions': [
                {u'id': 60840400,
                 u'indices': [0, 6],
                 u'id_str': u'60840400',
                 u'screen_name': u'aaloy',
                 u'name': u'Antoni Aloy'},
                {u'id': 552951614,
                 u'indices': [11, 21],
                 u'id_str': u'552951614',
                 u'screen_name': u'Pybonacci',
                 u'name': u'Pybonacci'},
                {u'id': 87322884,
                 u'indices': [60, 68],
                 u'id_str': u'87322884',
                 u'screen_name': u'dialelo',
                 u'name': u'Alejandro G\xf3mez'}
            ],
            u'hashtags': [
                {u'indices': [44, 51],
                 u'text': u'Python'},
                {u'indices': [52, 56],
                 u'text': u'IDE'}
            ],
            u'urls': [
                {u'url': u'http://t.co/5lTGNzba',
                 u'indices': [99, 119],
                 u'expanded_url':
                    u'http://sontek.net/turning-vim-into-a-modern-python-ide',
                 u'display_url': u'sontek.net/turning-vim-in\u2026'}
            ]}
        expected_result = [('attag', u'@aaloy'), u'  QT ',
                           ('attag', u'@Pybonacci'),
                           u': \xa1Qu\xe9 pasada con Vim! ',
                           ('hashtag', u'#Python'), u' ', ('hashtag', u'#IDE'),
                           u' RT ', ('attag', u'@dialelo'),
                           u' uso un setup parecido a este: ',
                           ('url', u'sontek.net/turning-vim-in\u2026')]

        status = create_status(text=text,
                               entities=entities)
        result = status.map_attributes(hashtag='hashtag',
                                       attag='attag',
                                       url='url')

        self.assertEqual(result, expected_result)

        text = (u'New release of #Turses 0.1.6 with lots of improvements, '
                u'ncurses twitter client. https://t.co/cciH85AG via @dialelo')
        entities = {
            u'hashtags': [{u'indices': [15, 22], u'text': u'Turses'}],
            u'urls': [{u'display_url': u'github.com/alejandrogomez\u2026',
                       u'expanded_url':
                            u'https://github.com/alejandrogomez/turses',
                       u'indices': [80, 101],
                       u'url': u'https://t.co/cciH85AG'}],
            u'user_mentions': [{u'id': 87322884,
                                u'id_str': u'87322884',
                                u'indices': [106, 114],
                                u'name': u'Alejandro G\xf3mez',
                                u'screen_name': u'dialelo'}]
        }
        expected_result = [u'New release of ',
                           ('hashtag', u'#Turses'),
                           (u' 0.1.6 with lots of improvements, '
                           u'ncurses twitter client. '),
                           ('url', u'github.com/alejandrogomez\u2026'),
                           u' via ',
                           ('attag', u'@dialelo')]

        status = create_status(user='nicosphere',
                               text=text,
                               entities=entities)
        result = status.map_attributes(hashtag='hashtag',
                                        attag='attag',
                                        url='url')

        self.assertEqual(result, expected_result)

    def test_map_attributes_to_retweet_with_hashtag(self):
        original_author = 'dialelo'
        original_text = 'I <3 #Python'
        original_status = create_status(user=original_author,
                                        text=original_text)

        text = 'RT @%s: %s' % (original_author, original_text)
        entities = {
            u'user_mentions': [],
            u'hashtags': [
                {u'indices': [5, 11],
                 u'text': u'Python'},
            ],
            u'urls': [],
            }
        retweet = create_status(text=text,
                                entities=entities,
                                is_retweet=True,
                                retweeted_status=original_status)

        # retweet text gets parsed because sometimes is not complete
        expected_result = [u'I ', u'<3 ', ('hashtag', '#Python')]
        result = retweet.map_attributes(hashtag='hashtag',
                                        attag='attag',
                                        url='url')

        self.assertEqual(result, expected_result)

    def test_map_attributes_mention(self):
        text = '@pypi is down!'

        entities = {
            u'user_mentions': [
                {u'id': 60840400,
                 u'indices': [0, 5],
                 u'id_str': u'60840400',
                 u'screen_name': u'pypi',
                 u'name': u'PYthon Package Index'},
            ],
            u'hashtags': [],
            u'urls': [],
            }
        tweet = create_status(text=text,
                              entities=entities,)

        expected_result = [('attag', u'@pypi'), u' is down!']
        result = tweet.map_attributes(hashtag='hashtag',
                                      attag='attag',
                                      url='url')

        self.assertEqual(result, expected_result)

    # properties

    def test_mentioned_usernames(self):
        user = 'turses'
        mentioned = ('dialelo', 'mental_floss', '4n_4Wfu1_US3RN4M3')

        expected_output = list(mentioned)

        text = "@%s, @%s and @%s" % mentioned
        status = create_status(user=user,
                               text=text)

        expected = set(expected_output)
        mentioned_usernames = status.mentioned_usernames
        self.assertEqual(expected, set(mentioned_usernames))

    def test_mentioned_for_reply(self):
        user = 'turses'
        mentioned = ('dialelo', 'mental_floss', '4n_4Wfu1_US3RN4M3')

        expected_output = list(mentioned)
        expected_output.append(user)
        expected_output = map(prepend_at, expected_output)

        text = "@%s, @%s and @%s" % mentioned
        status = create_status(user=user,
                               text=text)

        expected = set(filter(prepend_at, expected_output))
        mentioned_for_reply = status.mentioned_for_reply
        self.assertEqual(expected, set(mentioned_for_reply))

    def test_authors_username_tweet(self):
        user = 'turses'
        status = create_status(user=user)

        author = status.authors_username

        self.assertEqual(user, author)

    def test_authors_username_retweet(self):
        user = 'turses'
        status = create_status(user=user)
        retweeter = 'bot'
        retweet = create_status(user=retweeter,
                                is_retweet=True,
                                retweeted_status=status,
                                author=user)

        author = retweet.authors_username

        self.assertEqual(user, author)

    def test_authors_username_dm(self):
        user = 'turses'
        dm = create_direct_message(sender_screen_name=user,)

        author = dm.authors_username

        self.assertEqual(user, author)

    def test_dm_recipients_username_tweet(self):
        # authenticating user
        user = 'turses'

        # given a status in which the author is the authenticated author
        # must return `None`
        status = create_status(user=user)
        recipient_own_tweet = status.dm_recipients_username(user)
        self.failIf(recipient_own_tweet)

    def test_dm_recipients_username_dm(self):
        # authenticating user
        user = 'turses'

        # @user -> @another_user messages should return 'another_user'
        expected_recipient = 'dialelo'
        dm = create_direct_message(sender_screen_name=user,
                                   recipient_screen_name=expected_recipient,)
        recipient_dm_user_is_sender = dm.dm_recipients_username(user)
        self.assertEqual(recipient_dm_user_is_sender, expected_recipient)

        # @another_user -> @user messages should return 'another_user'
        dm = create_direct_message(sender_screen_name=expected_recipient,
                                   recipient_screen_name=user,)
        recipient_dm_user_is_recipient = dm.dm_recipients_username(user)
        self.assertEqual(recipient_dm_user_is_recipient, expected_recipient)

    def test_hashtags(self):
        user = 'turses'
        hashtags = ('#turses', '#arch_linux', '#I<3Python')

        expected_output = list(hashtags)

        text = "%s %s %s" % hashtags
        status = create_status(user=user,
                               text=text)

        expected = set(expected_output)
        mentioned_hashtags = status.hashtags
        self.assertEqual(expected, set(mentioned_hashtags))


class TimelineTest(ActiveListTest):

    def setUp(self):
        self.timeline = Timeline()
        self.assert_null_index()

    def active_index(self):
        return self.timeline.active_index

    # unique elements

    def test_unique_statuses_in_timeline(self):
        status = create_status()

        self.timeline.add_status(status)
        self.timeline.add_status(status)

        self.assertEqual(len(self.timeline), 1)

    # active index

    def test_active_index_is_0_when_creating_timeline_with_statuses(self):
        status = create_status()

        self.timeline = Timeline(statuses=[status])

        self.assertEqual(self.timeline.active_index, 0)

    def test_active_index_becomes_0_when_adding_first_status(self):
        status = create_status()

        self.timeline.add_status(status)

        self.assertEqual(self.timeline.active_index, 0)

    def test_active_index_does_not_change_when_adding_various_statuses(self):
        a_status = create_status(id=1)
        another_status = create_status(id=2)

        # first
        self.timeline.add_status(a_status)
        self.assertEqual(self.timeline.active_index, 0)

        # second
        self.timeline.add_status(another_status)
        self.assertEqual(self.timeline.active_index, 0)

    # insertion

    def test_insert_different_statuses_individually(self):
        old_status = create_status(created_at=datetime(1988, 12, 19))
        new_status = create_status(id=2)

        # first
        self.timeline.add_status(old_status)
        self.assertEqual(len(self.timeline), 1)

        # second
        self.timeline.add_status(new_status)
        self.assertEqual(len(self.timeline), 2)

    def test_insert_different_statuses(self):
        old_status = create_status(created_at=datetime(1988, 12, 19))
        new_status = create_status(id=2)

        self.timeline.add_statuses([old_status, new_status])

        self.assertEqual(len(self.timeline), 2)

    # order

    def test_statuses_ordered_reversely_by_date(self):
        old_status = create_status(created_at=datetime(1988, 12, 19))
        new_status = create_status(id=2)

        # ordered
        self.timeline = Timeline(statuses=[new_status, old_status])
        self.assertEqual(self.timeline[0], new_status)
        self.assertEqual(self.timeline[1], old_status)

        # unordered
        self.timeline = Timeline(statuses=[old_status, new_status])
        self.assertEqual(self.timeline[0], new_status)
        self.assertEqual(self.timeline[1], old_status)

    # unread

    def test_unread_count(self):
        self.assertEqual(self.timeline.unread_count, 0)

        # a status
        status = create_status(id=1)
        self.timeline.add_status(status)
        self.assertEqual(self.timeline.unread_count, 1)

        self.timeline.mark_all_as_read()
        self.assertEqual(self.timeline.unread_count, 0)

        # new statuses
        statuses = [create_status(id=id_num) for id_num in xrange(2, 10)]
        self.timeline.add_statuses(statuses)
        self.assertEqual(self.timeline.unread_count, len(statuses))

        self.timeline.mark_all_as_read()
        self.assertEqual(self.timeline.unread_count, 0)

    # clear

    def test_clear(self):
        old_created_at = datetime(1988, 12, 19)
        old_status = create_status(created_at=old_created_at)
        new_created_at = datetime.now()
        new_status = create_status(id=2,
                                   created_at=new_created_at)

        self.timeline.add_statuses([old_status, new_status])

        self.timeline.clear()

        self.assertEqual(len(self.timeline), 0)

    # update function related

    def test_extract_with_no_args(self):
        mock = MagicMock(name='update')

        timeline = Timeline(update_function=mock,)

        self.assertEqual(timeline._args, [])
        self.assertEqual(timeline._kwargs, {})

    def test_only_args(self):
        mock = MagicMock(name='update')
        args = 'python', 42

        timeline = Timeline(update_function=mock,
                            update_function_args=args,)

        self.assertEqual(timeline._args, list(args))
        self.assertEqual(timeline._kwargs, {})

    def test_with_only_kwargs(self):
        mock = MagicMock(name='update')
        kwargs = {'python': 'rocks'}

        timeline = Timeline(update_function=mock,
                            update_function_kwargs=kwargs)

        self.assertEqual(timeline._args, [])
        self.assertEqual(timeline._kwargs, kwargs)

    def test_with_both_args_and_kwargs(self):
        mock = MagicMock(name='update')
        args = 'python', 42
        kwargs = {'python': 'rocks'}

        timeline = Timeline(update_function=mock,
                            update_function_args=args,
                            update_function_kwargs=kwargs)

        self.assertEqual(timeline._args, list(args))
        self.assertEqual(timeline._kwargs, kwargs)

    # update invocation

    def test_update_with_no_args(self):
        mock = MagicMock(name='update')
        timeline = Timeline(update_function=mock,)

        timeline.update()

        mock.assert_called_once_with()

    def test_update_with_one_arg(self):
        mock = MagicMock(name='update')
        arg = '#python'
        timeline = Timeline(update_function=mock,
                            update_function_args=arg)

        timeline.update()

        mock.assert_called_once_with(arg)

    def test_update_with_multiple_args(self):
        mock = MagicMock(name='update')
        args = '#python', '#mock'
        timeline = Timeline(update_function=mock,
                            update_function_args=args)
        timeline.update()

        args = list(args)
        mock.assert_called_once_with(*args)

    def test_update_with_kwargs(self):
        mock = MagicMock(name='update')
        kwargs = {'text': '#python', 'action': 'search'}
        timeline = Timeline(update_function=mock,
                            update_function_kwargs=kwargs)
        timeline.update()

        mock.assert_called_once_with(**kwargs)

    def test_update_with_args_and_kwargs(self):
        mock = MagicMock(name='update')
        args = 'twitter', 42
        kwargs = {'text': '#python', 'action': 'search'}
        update_args = list(args)
        update_args.append(kwargs)

        timeline = Timeline(update_function=mock,
                            update_function_args=args,
                            update_function_kwargs=kwargs)
        timeline.update()

        args = list(args)
        mock.assert_called_once_with(*args, **kwargs)

    def test_update_with_no_args_extra_kwargs(self):
        mock = MagicMock(name='update')
        extra_kwargs = {'python': 'rocks'}

        timeline = Timeline(update_function=mock,)
        timeline.update(**extra_kwargs)

        mock.assert_called_once_with(**extra_kwargs)

    def test_update_with_one_arg_extra_kwargs(self):
        mock = MagicMock(name='update')
        arg = '#python'
        extra_kwargs = {'python': 'rocks'}

        timeline = Timeline(update_function=mock, update_function_args=arg)
        timeline.update(**extra_kwargs)

        mock.assert_called_once_with(arg, **extra_kwargs)

    def test_update_with_multiple_args_extra_kwargs(self):
        mock = MagicMock(name='update')
        args = ('#python', '#mock')
        extra_kwargs = {'python': 'rocks'}

        timeline = Timeline(update_function=mock,
                            update_function_args=args)
        timeline.update(**extra_kwargs)

        args = list(args)
        mock.assert_called_once_with(*args, **extra_kwargs)

    def test_update_with_kwargs_extra_kwargs(self):
        mock = MagicMock(name='update')
        kwargs = {'text': '#python', 'action': 'search'}
        extra_kwargs = {'text': 'rocks'}

        timeline = Timeline(update_function=mock,
                            update_function_kwargs=kwargs)
        timeline.update(**extra_kwargs)

        args = kwargs.copy()
        args.update(extra_kwargs)
        mock.assert_called_once_with(**args)

    def test_update_with_args_and_kwargs_extra_kwargs(self):
        mock = MagicMock(name='update')
        args = 'twitter', 42
        kwargs = {'text': '#python', 'action': 'search'}
        extra_kwargs = {'text': 'rocks'}

        timeline = Timeline(update_function=mock,
                            update_function_args=args,
                            update_function_kwargs=kwargs)
        timeline.update(**extra_kwargs)

        args = list(args)
        kwargs = kwargs.copy()
        kwargs.update(extra_kwargs)
        mock.assert_called_once_with(*args, **kwargs)


class TimelineListTest(ActiveListTest):

    def active_index(self):
        return self.timeline_list.active_index

    # - Helpers ---------------------------------------------------------------

    def append_timeline(self):
        self.timeline_list.append_timeline(Timeline('Timeline'))

    def assert_visible(self, visible_list):
        self.assertEqual(self.timeline_list.visible, visible_list)

    # - Tests -----------------------------------------------------------------

    def setUp(self):
        self.timeline_list = TimelineList()

    def test_has_timelines_false_if_empty(self):
        self.failIf(self.timeline_list.has_timelines())

    def test_has_timelines_true_otherwise(self):
        self.append_timeline()
        self.failUnless(self.timeline_list.has_timelines())

    def test_null_index_with_no_timelines(self):
        self.assert_null_index()

    def test_active_index_0_when_appending_first_timeline(self):
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_previous(self):
        # null index when there are no timelines
        self.timeline_list.activate_previous()
        self.assert_null_index()
        # does not change if its the first
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_next(self):
        # null index when there are no timelines
        self.timeline_list.activate_next()
        self.assert_null_index()
        # does not change if its the last
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_previous_and_activate_next(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        # next
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.timeline_list.activate_next()
        self.assertEqual(self.timeline_list.active_index, 2)
        # previous
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.timeline_list.activate_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_active_returns_first_appended(self):
        # append
        name = 'Timeline'
        timeline = Timeline(name)
        self.timeline_list.append_timeline(timeline)
        # assert
        active_timeline = self.timeline_list.active
        self.assertEqual(timeline, active_timeline)

    def test_active_returns_None_when_empty(self):
        self.assertIsNone(self.timeline_list.active)

    def test_append_timeline_increases_timeline_size(self):
        self.assertEqual(len(self.timeline_list), 0)
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 1)
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 2)

    def test_activate_first(self):
        # null index when there are no timelines
        self.timeline_list.activate_first()
        self.assert_null_index()
        # does not change if its the first
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_first()
        self.assertEqual(self.timeline_list.active_index, 0)
        # moves to the first when in another position
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.activate_next()
        self.timeline_list.activate_next()
        self.timeline_list.activate_first()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_activate_last(self):
        # null index when there are no timelines
        self.timeline_list.activate_last()
        self.assert_null_index()
        # does not change if its the last
        self.append_timeline()
        self.assertEqual(self.timeline_list.active_index, 0)
        self.timeline_list.activate_last()
        self.assertEqual(self.timeline_list.active_index, 0)
        # moves to the last when in another position
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.activate_last()
        self.assertEqual(self.timeline_list.active_index, 2)

    def test_shift_active_previous(self):
        # null index when there are no timelines
        self.timeline_list.shift_active_previous()
        self.assert_null_index()
        # does not change if its the first
        self.append_timeline()
        self.timeline_list.shift_active_previous()
        self.assertEqual(self.timeline_list.active_index, 0)

    def test_shift_active_next(self):
        # null index when there are no timelines
        self.timeline_list.shift_active_next()
        self.assert_null_index()
        # does not change if its the last
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 0)
        # it increases until reaching the end
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 1)
        self.append_timeline()
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 2)
        self.timeline_list.shift_active_next()
        self.assertEqual(self.timeline_list.active_index, 2)

    # visibility

    def test_no_visible_when_newly_created(self):
        self.assert_visible([])
        self.timeline_list.expand_visible_previous()

    def test_only_visible_is_index_0_when_appending_first_timeline(self):
        self.append_timeline()
        self.assert_visible([0])

    def test_expand_visible_previous(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.assert_visible([0])
        self.timeline_list.activate_last()
        self.assert_visible([2])

        self.timeline_list.expand_visible_previous()
        self.assert_visible([1, 2])
        self.timeline_list.expand_visible_previous()
        self.assert_visible([0, 1, 2])

        # there are no more timelines
        self.timeline_list.expand_visible_previous()
        self.assert_visible([0, 1, 2])

    def test_expand_visible_next(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.assert_visible([0])

        self.timeline_list.expand_visible_next()
        self.assert_visible([0, 1])
        self.timeline_list.expand_visible_next()
        self.assert_visible([0, 1, 2])

        # there are no more timelines
        self.timeline_list.expand_visible_next()
        self.assert_visible([0, 1, 2])

    def test_shrink_visible_beggining(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.activate_last()
        self.timeline_list.expand_visible_previous()
        self.timeline_list.expand_visible_previous()
        self.assert_visible([0, 1, 2])

        self.timeline_list.shrink_visible_beggining()
        self.assert_visible([1, 2])
        self.timeline_list.shrink_visible_beggining()
        self.assert_visible([2])

        # at least the active timeline has to be visible
        self.timeline_list.shrink_visible_beggining()
        self.assert_visible([2])

    def test_shrink_visible_end(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()
        self.assert_visible([0, 1, 2])

        self.timeline_list.shrink_visible_end()
        self.assert_visible([0, 1])
        self.timeline_list.shrink_visible_end()
        self.assert_visible([0])

        # at least the active timeline has to be visible
        self.timeline_list.shrink_visible_end()
        self.assert_visible([0])

    def test_visible_active_only_when_activating_invisible_timeline(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.expand_visible_next()
        self.assert_visible([0, 1])

        self.timeline_list.activate_last()
        self.assert_visible([2])

        self.timeline_list.expand_visible_previous()
        self.assert_visible([1, 2])

        self.timeline_list.activate_first()
        self.assert_visible([0])

    def test_consistent_visible_timelines_when_deleting_leftmost_active(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0, 1, 2])

        self.timeline_list.delete_active_timeline()

        # active index does not change
        self.assertEqual(self.active_index(), 0)

        # visible
        self.assert_visible([0, 1])

        # relative index
        relative_index = self.timeline_list.active_index_relative_to_visible
        self.assertEqual(relative_index, 0)

    def test_consistent_visible_timelines_when_deleting_middle_active(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0, 1, 2, 3, 4])

        self.timeline_list.activate_next()
        self.timeline_list.activate_next()

        self.assertEqual(self.active_index(), 2)
        self.assert_visible([0, 1, 2, 3, 4])

        self.timeline_list.delete_active_timeline()

        # active index does not change
        self.assertEqual(self.active_index(), 2)

        # visible
        self.assert_visible([0, 1, 2, 3])

        # relative index
        relative_index = self.timeline_list.active_index_relative_to_visible
        self.assertEqual(relative_index, 2)

    def test_consistent_visible_timelines_when_deleting_rightmost_timeline(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 3)

        self.timeline_list.expand_visible_next()
        self.timeline_list.expand_visible_next()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0, 1, 2])

        self.timeline_list.activate_next()
        self.timeline_list.activate_next()

        self.assertEqual(self.active_index(), 2)
        self.assert_visible([0, 1, 2])

        self.timeline_list.delete_active_timeline()
        self.assertEqual(len(self.timeline_list), 2)

        # active index shifts left
        self.assertEqual(self.active_index(), 1)

        # visible
        self.assert_visible([0, 1])

        # relative index
        relative_index = self.timeline_list.active_index_relative_to_visible
        self.assertEqual(relative_index, 1)

    def test_delete_active_timeline_with_one_visible_timeline_in_the_left(self):
        self.append_timeline()
        self.append_timeline()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0])

        self.timeline_list.delete_active_timeline()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0])

    def test_delete_active_timeline_with_one_visible_timeline_in_the_middle(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()

        self.assertEqual(self.active_index(), 0)
        self.assert_visible([0])
        self.assertEqual(len(self.timeline_list), 5)

        self.timeline_list.activate_next()
        self.timeline_list.activate_next()
        
        self.assertEqual(self.active_index(), 2)
        self.assert_visible([2])

        self.timeline_list.delete_active_timeline()
        self.assertEqual(len(self.timeline_list), 4)

        self.assertEqual(self.active_index(), 2)
        self.assert_visible([2])

    def test_delete_active_timeline_with_one_visible_timeline_in_the_right(self):
        self.append_timeline()
        self.append_timeline()
        self.append_timeline()
        self.assertEqual(len(self.timeline_list), 3)

        self.timeline_list.activate_next()
        self.timeline_list.activate_next()

        self.assertEqual(self.active_index(), 2)
        self.assert_visible([2])

        self.timeline_list.delete_active_timeline()
        self.assertEqual(len(self.timeline_list), 2)

        self.assertEqual(self.active_index(), 1)
        self.assert_visible([1])


if __name__ == '__main__':
    unittest.main()
