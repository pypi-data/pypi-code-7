class Rewindable(object):
    def __init__(self, source=None, data=None, fn=None, off=None, tlen=None):
        self.source = source or fn(data, tlen, off)
        self.back = None
        self.data = data
        self.off = off
        self.tlen = tlen

    def __iter__(self):
        while True:
            yield self.next()

    def next(self):
        if self.back:
            out = self.back
            self.back = None
            return out

        return self.source.next()

    def rewind(self, value):
        self.back = value

