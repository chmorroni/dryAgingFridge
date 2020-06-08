
from collections import deque

class CircBuf:
    """ Simple circular buffer with max length """

    def __init__(self, max_len):
        self.buf = deque(maxlen=max_len)

    def push(self, item):
        """ Insert new item, overwriting oldest item on overflow """

        self.buf.append(item)

    def clear(self):
        self.buf.clear()

    def get_data(self):
        data = list(map(list, zip(*self.buf)))
        return data
        