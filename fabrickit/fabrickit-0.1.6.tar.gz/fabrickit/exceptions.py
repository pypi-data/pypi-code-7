class RemoteExecutionException(Exception):
    def __init__(self, result):
        super(RemoteExecutionException, self).__init__(result)
        self.result = result
