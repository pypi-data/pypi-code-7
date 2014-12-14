from collections import defaultdict

class Dict2(defaultdict):
    def __init__(self):
        super(Dict2, self).__init__(Dict2)

    __getattr__ = defaultdict.__getitem__
    __setatrr__ = defaultdict.__setitem__
    __repr__ = dict.__repr__
