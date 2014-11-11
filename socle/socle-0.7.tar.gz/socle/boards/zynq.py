
from socle.boards.generic import GenericBoard

class ZynqBoard(GenericBoard):
    NAME = "Zynq-7000"
    def __init__(self):
        pass
        
    @classmethod
    def match(cls, e):
        return e.HARDWARE == "Xilinx Zynq Platform"

