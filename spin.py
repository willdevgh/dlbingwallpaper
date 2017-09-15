#! python 3
# --*-- encoding: UTF-8 --*--

import asyncio
import itertools
import sys


class Spin:
    '''running... [spin]'''
    def __init__(self, msg='running...', behind=True):
        self._msg = msg
        self._behind = behind
        self._spinner = None

    async def __run(self):
        write, flush = sys.stdout.write, sys.stdout.flush
        for char in itertools.cycle('|/-\\'):
            if self._behind:  status = self._msg + ' ' + char
            else:   status = char + ' ' + self._msg
            backward_len = len(status)
            write(status)
            flush()
            write('\x08' * backward_len)
            try:
                await asyncio.sleep(.1)
            except asyncio.CancelledError:
                break
        write(' ' * backward_len + '\x08' * backward_len)
        asyncio.get_event_loop().stop()

    def run(self):
        self._spinner = asyncio.ensure_future(self.__run())

    def exit(self):
        self._spinner.cancel()
