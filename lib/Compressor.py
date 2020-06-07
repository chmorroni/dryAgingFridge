
import gpiozero
import time

class Compressor():
    def __init__(self, pins):
        self.pins = []
        for pin in pins:
            self.pins.append(gpiozero.DigitalOutputDevice(pin))
        self.off()

    def on(self):
        for pin in self.pins:
            pin.on()

    def off(self):
        for pin in self.pins:
            pin.off()

if __name__ == "__main__":
    pins = [2, 3, 4]
    compressor = Compressor(pins)
    while True:
        compressor.on()
        time.sleep(1)
        compressor.off()
        time.sleep(1)
