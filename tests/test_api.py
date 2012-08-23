# -*- coding: utf-8 -*-

from sys import path
path.append('../')
import unittest

from turses.api.base import AsyncApi
from turses.api.debug import MockApi
from turses.api.backends import TweepyApi


ACCESS_TOKEN = 'Yohohohoooo'
ACCESS_TOKEN_SECRET = 'Skull joke!'


class AsyncApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         AsyncApi(MockApi,
                  access_token_key=ACCESS_TOKEN,
                  access_token_secret=ACCESS_TOKEN_SECRET,)


class MockApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         MockApi(access_token_key=ACCESS_TOKEN,
                 access_token_secret=ACCESS_TOKEN_SECRET,)


class TweepyApiTest(unittest.TestCase):
    def test_that_implements_abstract_base_class(self):
         TweepyApi(access_token_key=ACCESS_TOKEN,
                   access_token_secret=ACCESS_TOKEN_SECRET,)
