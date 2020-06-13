
from collections import deque
from threading import Lock

class CircBuf:
    def __init__(self, max_len):
        self.buf = deque(maxlen=max_len)
        self.lock = Lock()

    def push(self, item):
        self.lock.acquire()
        self.buf.append(item)
        self.lock.release()

    def clear(self):
        self.lock.acquire()
        self.buf.clear()
        self.lock.release()

    def get_data(self):
        self.lock.acquire()
        data = list(map(list, zip(*self.buf)))
        self.lock.release()
        return data
        