class Tagged(object):
    def __init__(self, tag=None, data=None, off=0, tlen=0, typ=None):
        self.data = data
        self.off = off
        self.tlen = tlen
        self.tag = tag
        self.typ = typ

    def encode(self):
        return self.data[self.off:self.off + self.tlen]

    def match(self, tag):
        if self.tag == tag:
            return self


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


class Choice(object):
    @classmethod
    def match(cls, tag):
        for spec in cls.types:
            match = spec.match(tag)
            if match is not None:
                return match

    @classmethod
    def to_data(cls, triplet, parent):
        tag, _cls, content = triplet
        match = cls.match(tag)
        if match is None:
            raise ValueError("No matching spec for {} tag {}".format(content, tag))
        return match.to_data(triplet, parent)
