
class Compressor:
    def __init__(self, pins):
        self.off()
    
    def off(self):
        self.on_state = False
    
    def on(self):
        self.on_state = True
