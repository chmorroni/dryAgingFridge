
from datetime import datetime

class WaterAtomizer:
    def __init__(self, pin):
        self.last_run = datetime(2000, 1, 1, 0, 0, 0)

    def run(self):
        self.last_run = datetime.now()

    def time_since_last_run(self):
        elapsed = datetime.now() - self.last_run
        return elapsed.seconds
