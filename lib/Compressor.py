
import gpiozero
import time

class Compressor(gpiozero.DigitalOutputDevice):
    def __init__(self, pin):
        gpiozero.DigitalOutputDevice.__init__(self, pin)
        self.off()

if __name__ == "__main__":
    compressor = Compressor(0)
    while True:
        compressor.on()
        time.sleep(5)
        compressor.off()
        time.sleep(5)
