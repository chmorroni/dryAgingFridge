
from lib.AtmosphericSensor import AtmosphericSensor
from lib.Buffer import CircBuf
from lib.Compressor import Compressor
from lib.DoorSwitch import DoorSwitch
from lib.WaterAtomizer import WaterAtomizer

import csv
from datetime import datetime
import numpy
import os
import threading
import time


TEMPERATURE_CEIL_F = 40
TEMPERATURE_FLOOR_F = 32

HUMIDITY_TARGET_PERCENT = 60
ATOMIZER_RUN_DELAY_S = 5

SAMPLE_FREQ_HZ = 1
SAMPLE_BUFFER_LEN = 24 * 60 * 60 * SAMPLE_FREQ_HZ # store 24 hours worth of data

buffer = CircBuf(SAMPLE_BUFFER_LEN)
csv_filename = "data/data.csv"

sensors = [AtmosphericSensor(1, 0), AtmosphericSensor(1, 1), AtmosphericSensor(1, 2)]
compressor = Compressor(1) # TODO actual pin
door = DoorSwitch(2) # TODO actual pin
atomizer = WaterAtomizer(3) # TODO actual pin


def sample_periodic():
    # sample sensors
    door.isOpen()
    time = datetime.now()
    temp = numpy.average([sensors[0].getTemp(), sensors[1].getTemp(), sensors[2].getTemp()])
    humidity = numpy.average([sensors[0].getHumidity(), sensors[1].getHumidity(), sensors[2].getHumidity()])
    
    # save datapoint
    datapoint = (time, temp, humidity)
    buffer.push(datapoint)
    with open(csv_filename, 'a') as csv_file:
        csv_file.write("{:s}, {:.2f}, {:.2f}".format(time.strftime("%c"), temp, humidity))
        csv_file.write(os.linesep)

    # if needed, activate compressor/atomizer
    if temp > TEMPERATURE_CEIL_F:
        compressor.on()
    elif temp < TEMPERATURE_FLOOR_F:
        compressor.off()

    if (humidity < HUMIDITY_TARGET_PERCENT) and (atomizer.time_since_last_run() > ATOMIZER_RUN_DELAY_S):
        compressor.run()

    # schedule next sampling
    timer = threading.Timer(1 / SAMPLE_FREQ_HZ, sample_periodic)
    timer.daemon = True
    timer.start()


if __name__ == "__main__":
    # initialize file
    with open(csv_filename, 'w') as csv_file:
        csv_file.write("Time, Temperature (F), Humidity (%)")
        csv_file.write(os.linesep)

    # start periodic sampling
    timer = threading.Timer(1 / SAMPLE_FREQ_HZ, sample_periodic)
    timer.daemon = True
    timer.start()
