import array

ADDRESS_WIDTH = 13
DATA_ADDRESS_WIDTH = 8

class State:
    __slots__ = ('registers', 'data', 'pc')

    def __init__(self):
        self.registers = array.array('B', map(lambda x:0, range(0, 8)))
        self.data = array.array('B',
                map(lambda x:0, range(0, 2**DATA_ADDRESS_WIDTH)))
        self.pc = 0

    def freeze(self):
        return (tuple(self.registers), tuple(self.data), self.pc)
