
from socle.boards.sunxi import SunxiBoard

class Cubieboard2(SunxiBoard):
    NAME = "Cubieboard2"
    DEFAULT_FEX = "templates/cubieboard2.fex"
    
    def __init__(self):
        pass
        
    @classmethod
    def match(cls, e):
        return e.HARDWARE == "sun7i" and e.MEM_TOTAL <= 1048576
    
