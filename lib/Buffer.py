
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

        data = [{}, {}, {}, {}, {}, {}]

        data[0]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[1]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[2]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[3]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[4]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]
        data[5]["x"] = [date.strftime("%Y-%m-%d %X") for date in data_lists[0]]

        data[0]["y"] = data_lists[1]
        data[1]["y"] = data_lists[2]
        data[2]["y"] = data_lists[3]
        data[3]["y"] = data_lists[4]
        data[4]["y"] = data_lists[5]
        data[5]["y"] = data_lists[6]

        data[0]["name"] = "Sensor 1 Temperature (F)"
        data[1]["name"] = "Sensor 2 Temperature (F)"
        data[2]["name"] = "Sensor 3 Temperature (F)"
        data[3]["name"] = "Sensor 1 Humidity (%)"
        data[4]["name"] = "Sensor 2 Humidity (%)"
        data[5]["name"] = "Sensor 3 Humidity (%)"
        
        return data
        