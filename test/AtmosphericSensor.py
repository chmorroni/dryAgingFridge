
import random

class AtmosphericSensor:
    def __init__(self, bus_id, device_id):
        pass

    def close(self):
        pass

    def getTemp(self):
        return 38
        # return random.randrange(0, 80, 1)

    def getHumidity(self):
        return 70
        # return random.randrange(0, 100, 1)
