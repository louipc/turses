# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.utils import is_username, is_hashtag, sanitize_username


class UtilsTest(unittest.TestCase):
    """Tests for the functions contained in `turses.utils`."""
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

    def test_is_valid_status_text(self):
        pass

    def test_is_valid_search_text(self):
        pass




if __name__ == '__main__':
    unittest.main()
