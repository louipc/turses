# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.ui import StatusWidget, map_attributes, parse_attributes
from tests  import create_status, create_direct_message


class AttributeTest(unittest.TestCase):
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
        result = map_attributes(status,
                                hashtag='hashtag',
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
        result = map_attributes(status,
                                hashtag='hashtag',
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
        result = map_attributes(retweet,
                                hashtag='hashtag',
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
        result = map_attributes(tweet,
                                hashtag='hashtag',
                                attag='attag',
                                url='url')

        self.assertEqual(result, expected_result)
    
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


class StatusWidgetTest(unittest.TestCase):
    def test_create_with_status(self):
        # load the defaults
        status = create_status()
        StatusWidget(status)

    def test_create_with_direct_message(self):
        # load the defaults
        direct_message = create_direct_message()
        StatusWidget(direct_message)




if __name__ == '__main__':
    unittest.main()
