"""
Mind.Knowledge
by Jakov Mankas
aka. Knowledge
"""


def data_bytes(data):
    """
    function that data(number, string...) converts to bytes:
    0 - numbers(integers and floats)
    1 - strings
    2 - floating point
    3 - lists begining
    4 - lists ending
    """
    final = bytearray()
    if type(data) == str:
        final.append(1)  # starting number of strings
        for l in data:
            final.append(ord(l))
        final.append(1)  # ending number of strings
    elif type(data) == int:
        final.append(0)  # starting number of numbers
        for x in range(int(data / 250)):
            final.append(255)
            data -= 250
        final.append(data + 5)
        final.append(0)  # ending number of numbers
    elif type(data) == float:
        final.append(0)  # starting number of numbers
        for x in range(int(data / 250)):
            final.append(255)
            data -= 250
        final.append(int(data) + 5)
        data -= int(data)
        final.append(2)  # floating point (.) number
        for x in range(int(round(data, 3) * 1000 / 250)):
            final.append(255)
            data -= 0.250
        final.append(int(data * 1000) + 5)
        final.append(0)  # ending number of strings
    elif type(data) == list:
        final.append(3)  # starting number of lists
        for x in data:
            for bit in data_bytes(x):
                final.append(bit)
        final.append(4)  # ending number of lists
    return final


class Knowledge:
    """
    class for all data in programm
    """
    def __init__(self, filename):
        self.data = {}
        self.filename = filename + '.knw'
        self.save = bytearray()

    def __repr__(self):
        self.ret = ''
        for x in self.data:
            self.ret += str(x)
            self.ret += ' : '
            self.ret += str(self.data[x])
            self.ret += '\n'
        return self.ret[:-1]  # so last \n is deleted

    def add_data(self, key, info):
        self.key = key
        self.info = info
        self.data[self.key] = self.info

    def save_data(self):
        for thing in self.data:
            for bit in data_bytes(thing):
                self.save.append(bit)
            for bit in data_bytes(self.data[thing]):
                self.save.append(bit)
        with open(self.filename, 'wb') as output:
            output.write(self.save)


def bytes_data(binary):
    """
    function that bytes converts to data(numbers, strigns...)
    """
    thing = None
    decimal = False
    ret = None
    for x in binary:
        if thing == 'integer':
            if x == 0:
                thing = None
                decimal = False
                yield ret
                ret = None
            elif x == 2:
                decimal = True
            else:
                if decimal:
                    ret += x / 1000 + 0.005
                else:
                    ret += x - 5
        elif thing == 'string':
            if x == 1:
                thing = None
                yield ret
                ret = None
            else:
                ret += chr(x)
        elif thing == 'list':
            if x == 4:
                thing = None
                fin = []
                for b in bytes_data(ret):
                    fin.append(b)
                yield fin
                ret = None
            else:
                ret.append(x)
        else:
            if x == 0:
                thing = 'integer'
                ret = 0
            elif x == 1:
                thing = 'string'
                ret = ''
            elif x == 3:
                thing = 'list'
                ret = bytearray()


def load(filename):
    """function that loads saved data and returns Knowledge object"""
    with open(filename + '.knw', 'rb') as infile:
        a = bytearray(infile.read())
    res = Knowledge(filename)
    state = 'key'
    key = None
    data = None
    for x in bytes_data(a):
        if state == 'key':
            key = x
            state = 'data'
        else:
            data = x
            state = 'key'
            res.add_data(key, data)
            key = None
            data = None
    return res
