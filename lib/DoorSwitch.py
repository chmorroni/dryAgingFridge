
import gpiozero
import time

class DoorSwitch(gpiozero.Button):
    def __init__(self, pin):
        gpiozero.Button.__init__(self, pin, pull_up=True)

    def isOpen(self):
        return not self.is_pressed

if __name__ == "__main__":
    door = DoorSwitch(1)
    while True:
        if door.isOpen():
            print("State: open")
        else:
            print("State: closed")
        time.sleep(1)
