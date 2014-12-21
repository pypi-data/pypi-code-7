class Suspension(object):

  def __init__(self, doc, keys):
    self.__doc = doc
    self.__keys = keys
    self.__evaluated = None

  def substitute(self, string_keys, list_keys):
    return self

  def resume(self):
    if self.__evaluated is None:
      self.__doc.evaluate_feature_keys(self.__keys)
      self.__doc.substitute()
      self.__evaluated = self.__doc.obj()

    return self.__evaluated


class DictSuspension(object):

  def __init__(self, doc, keys):
    self.__doc = doc
    self.__keys = keys
    self.__evaluated = {}

  def __getitem__(self, item):
    if item not in self.__evaluated:
      doc = self.__doc.clone()
      doc.env['_LAZY_LOOKUP_KEY'] = item
      doc.substitute()
      doc.evaluate_feature_keys(self.__keys)

      self.__evaluated[item] = doc.obj()

    return self.__evaluated[item]


class Lazy(object):

  name = '_lazy'
  validator = None
  suspension_cls = Suspension
  
  def __init__(self, loader):
    self.loader = loader

  def eval(self, doc, arg):
    return doc.make(Suspension(doc.make(arg), self.loader.keys))


class LazyLookup(Lazy):

  name = '_lazy_lookup'
  suspension_cls = DictSuspension
