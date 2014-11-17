class OXRError(Exception):
    def __init__(self, message=None, status=None, description=None):
        super(OXRError, self).__init__(message)
        self.status = status
        self.description = description
