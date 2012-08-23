# -*- coding: utf-8 -*-

"""
Contains `MockApi`, a fake `turses.api.ApiAdapter` implementation for debugging
purposes.
"""

import random
from time import sleep
from datetime import datetime

from turses.models import User, Status
from turses.meta import wrap_exceptions
from turses.api.base import ApiAdapter


def random_status(quantity=1, **kwargs):
    """Return `quantity` random statuses.

    By default it returns a single `turses.models.Status` instance, but
    if `q` is greater than 1 it returns a list of random statuses."""
    def create_status():
        sleep(0.02)
        now = datetime.now()
        defaults = {
            'id': random.randint(0, 999),
            'created_at': now,
            'user': 'testbot',
            'text': 'Status created at %s' % now,
        }
        defaults.update(**kwargs)

        return Status(**defaults)

    if not quantity:
        return

    if quantity == 1:
        return create_status()

    return [create_status() for _ in range(0, quantity)]


def random_user(quantity=1, **kwargs):
    """Return `quantity` random users.

    By default it returns a single `turses.models.user` instance, but
    if `q` is greater than 1 it returns a list of random users."""
    def create_user():
        sleep(0.02)
        now = datetime.now()
        defaults = {
            'id': random.randint(0, 999),
            'name': 'Alejandro',
            'screen_name': 'dialelo',
            'description': None,
            'url': 'http://dialelo.com',
            'created_at': now,
            'friends_count': 3,
            'followers_count': 42,
            'favorites_count': 0,
            'status': random_status(),
        }
        defaults.update(**kwargs)

        return User(**defaults)

    if not quantity:
        return

    if quantity == 1:
        return create_user()

    return [create_user() for _ in range(0, quantity)]


class MockApi(ApiAdapter):
    """
    """
    def __init__(self, *args, **kwargs):
        ApiAdapter.__init__(self, *args, **kwargs)

    @wrap_exceptions
    def init_api(self):
        self.is_authenticated = True

    def verify_credentials(self):
        return random_user()

    # users

    def get_user(self, screen_name):
        return random_user(screen_name=screen_name)

    # timelines

    def get_status(self, status_id):
        return random_status(id=status_id)

    def get_home_timeline(self):
        return random_status(quantity=3)

    def get_user_timeline(self, screen_name):
        return random_status(quantity=10)

    def get_own_timeline(self):
        return random_status(quantity=10)

    def get_mentions(self):
        return random_status(quantity=10)

    def get_favorites(self):
        return random_status(quantity=10)

    def get_direct_messages(self):
        # TODO: random DM
        return random_status(quantity=10)

    def get_thread(self, status):
        return random_status(quantity=14)

    def get_message_thread(self, status):
        return random_status(quantity=4)

    def search(self, text):
        return random_status(quantity=14)

    def get_retweets_of_me(self):
        return random_status(quantity=14)

    # statuses

    def update(self, text):
        pass

    def retweet(self, status):
        pass

    def destroy_status(self, status):
        """
        Destroy the given `status` (must belong to authenticating user).
        """
        pass

    def direct_message(self, screen_name, text):
        pass

    def destroy_direct_message(self, dm):
        """
        Destroy the given `dm` (must be written by the authenticating user).
        """
        pass

    # friendship

    def create_friendship(self, screen_name):
        pass

    def destroy_friendship(self, screen_name):
        pass

    # favorite methods

    def create_favorite(self, status):
        pass

    def destroy_favorite(self, status):
        pass

    # list methods

    def get_lists(self, screen_name):
        pass

    def get_own_lists(self):
        pass

    def get_list_memberships(self):
        pass

    def get_list_subscriptions(self):
        pass

    def get_list_timeline(self, list):
        pass

    def get_list_members(self, list):
        pass

    def is_list_member(self, user, list):
        pass

    def subscribe_to_list(self, list):
        pass

    def get_list_subscribers(self, list):
        pass

    def is_list_subscriber(self, user, list):
        pass
