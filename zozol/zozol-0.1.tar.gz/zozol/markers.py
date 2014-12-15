class Tagged(object):
    def __init__(self, tag=None, data=None, off=0, tlen=0, typ=None):
        self.data = data
        self.off = off
        self.tlen = tlen
        self.tag = tag
        self.typ = typ


class Implicit(Tagged):
    pass

class Explicit(Tagged):
    pass


class Optional(object):
    def __init__(self, typ):
        self.typ = typ


class Default(object):
    def __init__(self, value, typ):
        self.value = value
        self.typ = typ


