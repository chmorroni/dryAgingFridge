
from BME280 import BME280

import spidev
import time

class AtmosphericSensor:
    def __init__(self, bus_id, device_id):
        self.bus_id = bus_id
        self.device_id = device_id
        self.spi = spidev.SpiDev()
        self.spi.open(bus_id, device_id)
        self.spi.max_speed_hz = 10000
        self.spi.bits_per_word = 8
        self.device = BME280(self.spi)

    def close(self):
        self.spi.close()

    def getTemp(self):
        return self.device.read_temperature_f()

    def getHumidity(self):
        return self.device.read_humidity()

if __name__ == "__main__":
    sensors = []
    sensors.append(AtmosphericSensor(1, 0))
    sensors.append(AtmosphericSensor(1, 1))
    sensors.append(AtmosphericSensor(1, 2))
    while True:
        for i in range(0, 3):
            print("Sensor {:d} Temp: {:.3f} F, Humidity: {:.3f}%".format(i, sensors[i].getTemp(), sensors[i].getHumidity()))
        time.sleep(1)

