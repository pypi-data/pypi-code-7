class Rewindable(object):
    def __init__(self, source):
        self.source = source
        self.back = None

    def __iter__(self):
        while True:
            return self.next()

    def next(self):
        if self.back:
            out = self.back
            self.back = None
            return out

        return next(self.source)

    def rewind(self, value):
        self.back = value

