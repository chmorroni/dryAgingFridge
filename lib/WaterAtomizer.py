
from datetime import datetime
import gpiozero
import time

class WaterAtomizer(gpiozero.DigitalOutputDevice):
    def __init__(self, pin):
        gpiozero.DigitalOutputDevice.__init__(self, pin)
        self.off()
        self.last_run = datetime(2000, 1, 1, 0, 0, 0)

    def run(self):
        gpiozero.DigitalOutputDevice.blink(self, on_time=0.01, off_time=1, n=2, background=True)
        self.last_run = datetime.now()

    def time_since_last_run(self):
        elapsed = datetime.now() - self.last_run
        return elapsed.seconds

if __name__ == "__main__":
    atomizer = WaterAtomizer(0)
    while True:
        if atomizer.time_since_last_run() > 5:
            atomizer.run()
        time.sleep(1)
