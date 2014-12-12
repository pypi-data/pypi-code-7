class Message(object):

    def __init__(self, copy=None):
        if copy:
            self.init(copy.text)
            self.args = copy.args
            self.kwargs = copy.kwargs
        else:
            self.init(None)

    def init(self, text, *args, **kwargs):
        self.text = text
        self.args = args
        self.kwargs = kwargs

    def __call__(self):
        return self.translate().format(*self.args, **self.kwargs)

    def translate(self):
        return self.text
