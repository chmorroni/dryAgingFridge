
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

import lib.Accounts as Accounts
from lib.Buffer import CircBuf
from lib.Email import Email

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


TEMPERATURE_CEIL_F = 36
TEMPERATURE_FLOOR_F = 34
TEMPERATURE_WARNING_UPPER_F = 40
TEMPERATURE_WARNING_LOWER_F = 30

HUMIDITY_TARGET_PERCENT = 80
HUMIDITY_WARNING_UPPER_PERCENT = 100
HUMIDITY_WARNING_LOWER_PERCENT = 50
ATOMIZER_RUN_DELAY_S = 5

SAMPLE_FREQ_HZ = 1
SAMPLE_BUFFER_LEN = 24 * 60 * 60 * SAMPLE_FREQ_HZ # store 24 hours worth of data

MIN_EMAIL_PERIOD_S = 15 * 60 # 15 minutes


buffer = CircBuf(SAMPLE_BUFFER_LEN)
out_path = "data"
csv_filename = "data.csv"

sensors = [AtmosphericSensor(1, 0), AtmosphericSensor(1, 1), AtmosphericSensor(1, 2)]
compressor_pins = [2, 3, 4]
compressor = Compressor(compressor_pins)
door = DoorSwitch(1)
# atomizer = WaterAtomizer(3) # TODO actual pin
email = Email(MIN_EMAIL_PERIOD_S)


def sample_periodic():
    # sample sensors
    door.isOpen()
    time = datetime.now()
    temps = [sensors[0].getTemp(), sensors[1].getTemp(), sensors[2].getTemp()]
    temp = numpy.average(temps)
    humidities = [sensors[0].getHumidity(), sensors[1].getHumidity(), sensors[2].getHumidity()]
    humidity = numpy.average(humidities)
    
    # save datapoint
    datapoint = (time, temps[0], temps[1], temps[2], humidities[0], humidities[1], humidities[2])
    buffer.push(datapoint)
    with open(os.path.join(out_path, csv_filename), 'a') as csv_file:
        csv_file.write("{:s}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}\n".format(
            time.strftime("%Y-%m-%d %X"), temps[0], temps[1], temps[2], humidities[0], humidities[1], humidities[2])
        )

    # if needed, activate compressor/atomizer
    if temp > TEMPERATURE_CEIL_F:
        compressor.on()
    elif temp < TEMPERATURE_FLOOR_F:
        compressor.off()

    # if (humidity < HUMIDITY_TARGET_PERCENT) and (atomizer.time_since_last_run() > ATOMIZER_RUN_DELAY_S):
        # atomizer.run()

    # check warning bounds
    if (temp > TEMPERATURE_WARNING_UPPER_F) or (temp < TEMPERATURE_WARNING_LOWER_F):
        email.send_mail(Accounts.TO_EMAIL, "Refrigerator Temperature Out of Bounds", "Current temperature {:.3f} F".format(temp))
    if (humidity > HUMIDITY_WARNING_UPPER_PERCENT) or (humidity < HUMIDITY_WARNING_LOWER_PERCENT):
        email.send_mail(Accounts.TO_EMAIL, "Refrigerator Humidity Out of Bounds", "Current humidity {:.2f}%".format(humidity))

    # schedule next sampling
    timer = threading.Timer(1 / SAMPLE_FREQ_HZ, sample_periodic)
    timer.daemon = True
    timer.start()


## initialize webapp
app = Flask(__name__)
app.config["SECRET_KEY"] = Accounts.WEB_KEY
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
        csv_file.write("Time, Sensor 1 Temperature (F), Sensor 2 Temperature (F), Sensor 3 Temperature (F), Sensor 1 Humidity (%), Sensor 2 Humidity (%), Sensor 3 Humidity (%)\n")

    # start periodic sampling
    sample_periodic()
    
    socketio.run(app, host="0.0.0.0", port=5000)
