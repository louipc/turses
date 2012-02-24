###############################################################################
#                               coding=utf-8                                  #
#           Copyright (c) 2012 Nicolas Paris and Alejandro Gómez.             #
#       Licensed under the GPL License. See LICENSE.txt for full details.     #
###############################################################################

import urwid

class BufferListMotionKeyHandler(object):
    """Handles motion key bindings associated with a `BufferList`."""
    def __init__(self, bufferlist):
        self.bufferlist = bufferlist

    def handle(self, input, raw):
        clean_input = ''.join(input)
        #TODO
        if any([clean_input == 'q', clean_input == 'Q', clean_input == 'esc']):
            raise urwid.ExitMainLoop()
        elif clean_input == 'h':
            self.bufferlist.display_previous_buffer()
            self.bufferlist.update()
        elif clean_input == 'l':
            self.bufferlist.display_next_buffer()
            self.bufferlist.update()
        else:
            return input
