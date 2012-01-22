###############################################################################
#                               coding=utf-8                                  #
#                     Copyright (c) 2012 Alejandro Gómez.                     #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import sys
sys.path.append('..')

from credentials import *
from turses.api import Api

from twitter import TwitterError, Status, User

api = Api(consumer_key, consumer_secret, access_token_key, access_token_secret)
user = api.VerifyCredentials()
