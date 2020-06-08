
class Compressor:
    def __init__(self, pins):
        self.off()
    
    def off(self):
        self.is_on = False
    
    def on(self):
        self.is_on = True
