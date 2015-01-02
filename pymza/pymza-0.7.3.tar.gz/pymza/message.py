class SourceMessage(dict):
    def __init__(self, source, data):
        self.source = source
        dict.__init__(self, data)