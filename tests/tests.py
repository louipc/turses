from datetime import datetime
from time import sleep

from turses.models import Status, DirectMessage


def now():
    sleep(0.001)
    return datetime.now()


def create_status(**kwargs):
    defaults = {
        'id': 1,
        'created_at': now(),
        'user': 'testbot',
        'text': 'Status created at %s' % now,
    }
    defaults.update(**kwargs)

    return Status(**defaults)


def create_direct_message(**kwargs):
    defaults = {
        'id': 1,
        'created_at': now(),
        'sender_screen_name': 'Alice',
        'recipient_screen_name': 'Bob',
        'text': 'Direct Message at %s' % now,
    }
    defaults.update(kwargs)

    return DirectMessage(**defaults)
