
import random

class DoorSwitch:
    def __init__(self, pin):
        pass

    def isOpen(self):
        return random.randint(0, 1) == 1
