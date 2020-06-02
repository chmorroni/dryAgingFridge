
import gpiozero
import time

class DoorSwitch(gpiozero.Button):
    def __init__(self, pin):
        gpiozero.Button.__init__(self, pin, pull_up=True)

    def isOpen(self):
        return gpiozero.Button.is_pressed(self)

if __name__ == "__main__":
    door = DoorSwitch(0)
    while True:
        if door.isOpen():
            print("State: open")
        else:
            print("State: closed")
        time.sleep(1)
