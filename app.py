
from lib.AtmosphericSensor import AtmosphericSensor

import time

sensors = [AtmosphericSensor(1, 0), AtmosphericSensor(1, 1), AtmosphericSensor(1, 2)]

if __name__ == "__main__":
    while True:
        print("Reading sensors...")
        print("  0: Temp: {:.3f} F, Humidity: {:.3f}%".format(sensors[0].getTemp(), sensors[0].getHumidity()))
        print("  1: Temp: {:.3f} F, Humidity: {:.3f}%".format(sensors[1].getTemp(), sensors[1].getHumidity()))
        print("  2: Temp: {:.3f} F, Humidity: {:.3f}%".format(sensors[2].getTemp(), sensors[2].getHumidity()))
        time.sleep(1)

