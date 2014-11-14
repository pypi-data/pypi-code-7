from counter import Counter
from helper import Helper

class ComponentInput:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, fields):
    self._name = name
    self._type = "input"

    self._emits = ["stream_"+Counter.get()]
    self._fields = fields

    Helper.check_name("inputs", self._name, self._app._names)
    Helper.check_component_source(self)

  def run_operation(self):
    print "Component sources cannot be run!"
