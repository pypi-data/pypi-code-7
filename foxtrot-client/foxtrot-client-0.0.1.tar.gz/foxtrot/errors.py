class FoxtrotError(Exception):
  def __init__(self, message):
    super(FoxtrotError, self).__init__(message)

class ParameterError(FoxtrotError):
  def __init__(self, param):
    self.parameter = param
    super(ParameterError, self).__init__("Missing parameter: {}".format(param))

class APIResponseError(FoxtrotError):
  pass

class APITimeoutError(FoxtrotError):
  pass
