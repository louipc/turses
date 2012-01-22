###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

class Key(object):
    """Handles key bindings."""
    def __init__(self, bufferlist):
        self.bufferlist = bufferlist

    def handle(self, ch):
        #TODO
        if any([ch == 'q', ch == 'Q', ch == 'esc']):
            raise urwid.ExitMainLoop()
        elif ch == 'h':
            self.bufferlist.prev_buffer()
        elif ch == 'l':
            self.bufferlist.next_buffer()
