
import csv
from datetime import datetime
from flask import Flask, Response, render_template, g
from flask_socketio import SocketIO, emit, send
import json
import numpy
import os
from scipy.signal import butter, filtfilt
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
else:
    from lib.AtmosphericSensor import AtmosphericSensor
    from lib.Compressor import Compressor
    from lib.DoorSwitch import DoorSwitch


TEMPERATURE_CEIL_F = 36
TEMPERATURE_FLOOR_F = 34
TEMPERATURE_WARNING_UPPER_F = 40
TEMPERATURE_WARNING_LOWER_F = 30

HUMIDITY_TARGET_PERCENT = 80
ATOMIZER_RUN_DELAY_S = 5

SAMPLE_FREQ_HZ = 1
SAMPLE_BUFFER_LEN = 24 * 60 * 60 * SAMPLE_FREQ_HZ # store 24 hours worth of data

MIN_EMAIL_PERIOD_S = 15 * 60 # 15 minutes


buffer = CircBuf(SAMPLE_BUFFER_LEN)
out_path = "/var/log/dryAgingFridge"
csv_filename = "data_{:s}.csv".format(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))

sensors = [AtmosphericSensor(1, 0), AtmosphericSensor(1, 1), AtmosphericSensor(1, 2)]
compressor_pins = [2, 3, 4]
compressor = Compressor(compressor_pins)
door = DoorSwitch(1)
# atomizer = WaterAtomizer(3) # TODO actual pin
email = Email(MIN_EMAIL_PERIOD_S)
data_json = ""


def sample_periodic():
    # schedule next sampling
    timer = threading.Timer(1 / SAMPLE_FREQ_HZ, sample_periodic)
    timer.daemon = True
    timer.start()

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
    if door.isOpen() == True:
        email.send_mail(Accounts.TO_EMAIL, "Refrigerator Door Open", "Refrigerator door is currently open")


## initialize webapp
app = Flask(__name__)
app.config["SECRET_KEY"] = Accounts.WEB_KEY
socketio = SocketIO(app)

@app.route("/", methods = ["POST", "GET"])
def index():
    return render_template("index.html")


@app.route("/data")
def chart_data():
    def update_data():
        yield f"data:{data_json}\n\n"
        time.sleep(10)

    return Response(update_data(), mimetype="text/event-stream")


@socketio.on("data-request")
def send_last_data():
    global data_json
    emit("data-response", data_json)


def process_data():
    while True:
        start_time = time.process_time()

        raw_data = buffer.get_data()
        data = [{}, {}, {}]

        for line in data:
            line["x"] = [date.strftime("%Y-%m-%d %X") for date in raw_data[0]]

        data[1]["y"] = list(numpy.average(raw_data[1:4], axis=0))

        # LPF humidity
        humidity = numpy.average(raw_data[4:7], axis=0)
        data[0]["y"] = list(humidity)

        if len(humidity) > 15:
            b, a = butter(4, 1/512, btype='low', analog=False)
            data[2]["y"] = list(filtfilt(b, a, humidity))
        else:
            data[2]["y"] = list(humidity)

        data[0]["name"] = "Average Humidity (%)"
        data[1]["name"] = "Average Temperature (F)"
        data[2]["name"] = "Filtered Average Humidity (%)"

        # styling
        for line in data:
            line["mode"] = "lines"
            line["line"] = {}

        data[0]["showlegend"] = False

        data[0]["line"]["color"] = "#CED1FD"
        data[1]["line"]["color"] = "#EF553B"
        data[2]["line"]["color"] = "#636EFA"

        global data_json
        data_json = json.dumps(data)

        stop_time = time.process_time()
        print("Processed {:d} datapoints in {:.3f} seconds".format(len(raw_data[0]), stop_time - start_time))

        time.sleep(1)


if __name__ == "__main__":
    # initialize file
    if not os.path.exists(out_path):
        os.makedirs(out_path)

    with open(os.path.join(out_path, csv_filename), 'w') as csv_file:
        csv_file.write("Time, Sensor 1 Temperature (F), Sensor 2 Temperature (F), Sensor 3 Temperature (F), Sensor 1 Humidity (%), Sensor 2 Humidity (%), Sensor 3 Humidity (%), Compressor On\n")

    # start periodic sampling
    sample_periodic()

    processing_thread = threading.Thread(target=process_data, args=[], daemon=True)
    processing_thread.start()
    
    # start web app
    socketio.run(app, host="0.0.0.0", port=5000)
