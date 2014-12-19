
class SignalRequestData(object):
  """
      class to map posted form data to a nested dictionary structure
      this can be done when fields are named using a convention like:

        name1.name2.name3

  """
  __structDict = {}
  __delim = "_"

  def __init__(self, _d = None):
    if _d:
      [self.updateItem( {k : v} ) for (k, v) in _d.iteritems() ]

  def setDelimiter(self, delim):
    self.__delim = delim

  def _updateItem(self, _dict, keyList, value):
    """ recursively process the keyList to build the structure and assign the value
    """
    if len(keyList) == 1:
      _dict.update( { keyList[0] : value })
    else:
      if not _dict.has_key( keyList[0] ):
        _dict.update( {keyList[0] : dict() })
      self._updateItem( _dict[ keyList[0] ], keyList[1:], value )

  def updateItem(self, s):
    (key, value), = s.items()
    keyList = key.split(self.__delim)
    self._updateItem(self.__structDict, keyList, value)

  def __call__(self):
    return self.__structDict

