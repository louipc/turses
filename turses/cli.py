###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################


from util import parse_arguments
from config import Configuration
from controller import Turses
from ui.curses import CursesInterface


def main():
    configuration = Configuration(parse_arguments())
    ui = CursesInterface()
    Turses(configuration, ui)
