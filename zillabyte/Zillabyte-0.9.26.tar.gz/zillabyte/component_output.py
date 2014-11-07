from helper import Helper

class ComponentOutput:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, columns, relation, scope):
    self._name = name
    self._type = "output"
    self._columns = columns

    if relation != None:
      self._relation = relation
    else:
      self._relation = name
    self._scope = scope

    Helper.check_sink(self._name, self._columns, self._app._nodes, "outputs")

  def run_operation(self):
    print "Component sinks cannot be run!"
