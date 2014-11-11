
from socle.boards.generic import GenericBoard

class RaspberryPi(GenericBoard):
    NAME = "Raspberry Pi"

    def __init__(self):
        pass
        
    @classmethod
    def match(cls, e):
        return e.HARDWARE == "BCM2708"
