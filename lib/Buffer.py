
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
        data_lists = list(map(list, zip(*self.buf)))

        data = [{}, {}]
        data[0]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[1]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[0]["y"] = data_lists[1]
        data[1]["y"] = data_lists[2]
        data[0]["name"] = "Temperature (F)"
        data[1]["name"] = "Humidity (%)"
        
        return data
        