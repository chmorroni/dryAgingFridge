
from lib.BME280 import BME280

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
    sensor = AtmosphericSensor(1, 0)
    while True:
        print("Temp: {:.3f} F, Humidity: {:.3f}%".format(sensor.getTemp(), sensor.getHumidity()))
        time.sleep(1)
    sensor.close()

