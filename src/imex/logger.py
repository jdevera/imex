import sys

class SimpleScreenLogger(object):

    LEVEL_ERROR = 3
    LEVEL_WARNING = 3
    LEVEL_INFO = 2
    LEVEL_DEBUG = 1
    LEVEL_NOSY = 0

    def __init__(self, level=LEVEL_INFO):
        self._level = level
        self._out = sys.stdout
        self._queue = []

    def set_level(self, level):
        self._level = level

    def info(self, msg):
        if self._level <= self.LEVEL_INFO:
            print >> self._out, msg

    def debug(self, msg):
        if self._level <= self.LEVEL_DEBUG:
            print >> self._out, msg

    def qdebug(self, msg):
        if self._level <= self.LEVEL_DEBUG:
            self._queue.append((self.LEVEL_DEBUG, msg))

    def dump(self):
        while len(self._queue) > 0:
            level, msg = self._queue.pop(0)
            if self._level <= level:
                print >> self._out, msg
    def clear(self):
        self._queue = []
