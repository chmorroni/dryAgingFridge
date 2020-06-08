
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

    # if needed, activate compressor/atomizer
    if temp > TEMPERATURE_CEIL_F:
        compressor.on()
    elif temp < TEMPERATURE_FLOOR_F:
        compressor.off()

    # if (humidity < HUMIDITY_TARGET_PERCENT) and (atomizer.time_since_last_run() > ATOMIZER_RUN_DELAY_S):
        # atomizer.run()
    
    # save datapoint
    datapoint = (time, temps[0], temps[1], temps[2], humidities[0], humidities[1], humidities[2])
    buffer.push(datapoint)
    with open(os.path.join(out_path, csv_filename), 'a') as csv_file:
        csv_file.write("{:s}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:s}\n".format(
            time.strftime("%Y-%m-%d %X"), temps[0], temps[1], temps[2], humidities[0], humidities[1], humidities[2], str(compressor.is_on))
        )

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
    raw_data = buffer.get_data()
    
    data = [{}, {}, {}, {}, {}, {}, {}, {}]

    for line in data:
        line["x"] = [date.strftime("%Y-%m-%d %X") for date in raw_data[0]]

    data[0]["y"] = raw_data[1]
    data[1]["y"] = raw_data[2]
    data[2]["y"] = raw_data[3]
    data[3]["y"] = raw_data[4]
    data[4]["y"] = raw_data[5]
    data[5]["y"] = raw_data[6]
    data[6]["y"] = list(numpy.average(raw_data[1:4], axis=0))
    data[7]["y"] = list(numpy.average(raw_data[4:7], axis=0))

    data[0]["name"] = "Sensor 1 Temperature (F)"
    data[1]["name"] = "Sensor 2 Temperature (F)"
    data[2]["name"] = "Sensor 3 Temperature (F)"
    data[3]["name"] = "Sensor 1 Humidity (%)"
    data[4]["name"] = "Sensor 2 Humidity (%)"
    data[5]["name"] = "Sensor 3 Humidity (%)"
    data[6]["name"] = "Average Humidity (%)"
    data[7]["name"] = "Average Temperature (F)"

    # styling
    for line in data:
        line["mode"] = "lines"
        line["line"] = {}

    for line in data[0:6]:
        line["showlegend"] = False

    data[0]["line"]["color"] = "#FBD6D0"
    data[1]["line"]["color"] = "#FBD6D0"
    data[2]["line"]["color"] = "#FBD6D0"
    data[3]["line"]["color"] = "#CED1FD"
    data[4]["line"]["color"] = "#CED1FD"
    data[5]["line"]["color"] = "#CED1FD"
    data[6]["line"]["color"] = "#EF553B"
    data[7]["line"]["color"] = "#636EFA"

    data_json = json.dumps(data)
    emit("data-response", data_json)


if __name__ == "__main__":
    # initialize file
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(os.path.join(out_path, csv_filename), 'w') as csv_file:
        csv_file.write("Time, Sensor 1 Temperature (F), Sensor 2 Temperature (F), Sensor 3 Temperature (F), Sensor 1 Humidity (%), Sensor 2 Humidity (%), Sensor 3 Humidity (%), Compressor On\n")

    # start periodic sampling
    sample_periodic()
    
    socketio.run(app, host="0.0.0.0", port=5000)
