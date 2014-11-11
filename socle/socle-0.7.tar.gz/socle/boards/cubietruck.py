
from socle.boards.sunxi import SunxiBoard

class Cubietruck(SunxiBoard):
    NAME = "Cubietruck"
    DEFAULT_FEX = "templates/cubietruck.fex"
        
    @classmethod
    def match(cls, e):
        return e.HARDWARE == "sun7i" and e.MEM_TOTAL > 1048576
    
    def reset(self):
        super(Cubietruck, self).reset()
        self.fex.set("uart_para4", "uart_tx", "port:PG10<4><1><default><default>")
        self.fex.set("uart_para4", "uart_rx", "port:PG11<4><1><default><default>")

