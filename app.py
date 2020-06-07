
import csv
from datetime import datetime
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
import numpy
import os
import sys
import threading
import time

from lib.Buffer import CircBuf

if (len(sys.argv) > 1) and (sys.argv[1] == "-test"):
    print("Using mock I/O")
    from test.AtmosphericSensor import AtmosphericSensor
    from test.Compressor import Compressor
    from test.DoorSwitch import DoorSwitch
    from test.WaterAtomizer import WaterAtomizer
else:
    from lib.AtmosphericSensor import AtmosphericSensor
    from lib.Compressor import Compressor
    from lib.DoorSwitch import DoorSwitch
    from lib.WaterAtomizer import WaterAtomizer


TEMPERATURE_CEIL_F = 40
TEMPERATURE_FLOOR_F = 32

HUMIDITY_TARGET_PERCENT = 60
ATOMIZER_RUN_DELAY_S = 5

SAMPLE_FREQ_HZ = 1
SAMPLE_BUFFER_LEN = 24 * 60 * 60 * SAMPLE_FREQ_HZ # store 24 hours worth of data


buffer = CircBuf(SAMPLE_BUFFER_LEN)
out_path = "data"
csv_filename = "data.csv"

sensors = [AtmosphericSensor(1, 0), AtmosphericSensor(1, 1), AtmosphericSensor(1, 2)]
compressor_pins = [2, 3, 4]
compressor = Compressor(pins)
door = DoorSwitch(1)
# atomizer = WaterAtomizer(3) # TODO actual pin


def sample_periodic():
    # sample sensors
    door.isOpen()
    time = datetime.now()
    temp = numpy.average([sensors[0].getTemp(), sensors[1].getTemp(), sensors[2].getTemp()])
    humidity = numpy.average([sensors[0].getHumidity(), sensors[1].getHumidity(), sensors[2].getHumidity()])
    
    # save datapoint
    datapoint = (time, temp, humidity)
    buffer.push(datapoint)
    with open(os.path.join(out_path, csv_filename), 'a') as csv_file:
        csv_file.write("{:s}, {:.2f}, {:.2f}\n".format(time.strftime("%Y-%m-%d %X"), temp, humidity))

    # if needed, activate compressor/atomizer
    if temp > TEMPERATURE_CEIL_F:
        compressor.on()
    elif temp < TEMPERATURE_FLOOR_F:
        compressor.off()

    # if (humidity < HUMIDITY_TARGET_PERCENT) and (atomizer.time_since_last_run() > ATOMIZER_RUN_DELAY_S):
        # atomizer.run()

    # schedule next sampling
    timer = threading.Timer(1 / SAMPLE_FREQ_HZ, sample_periodic)
    timer.daemon = True
    timer.start()


## initialize webapp
app = Flask(__name__)
app.config["SECRET_KEY"] = "qwerty"
socketio = SocketIO(app)

@app.route("/", methods = ["POST", "GET"])
def line():
    return render_template("index.html")


## event handlers
@socketio.on("data-request")
def send_data():
    data_json = json.dumps(buffer.get_data())
    emit("data-response", data_json)


if __name__ == "__main__":
    # initialize file
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(os.path.join(out_path, csv_filename), 'w') as csv_file:
        csv_file.write("Time, Temperature (F), Humidity (%)\n")

    # start periodic sampling
    sample_periodic()
    
    socketio.run(app, host="0.0.0.0", port=5000)
