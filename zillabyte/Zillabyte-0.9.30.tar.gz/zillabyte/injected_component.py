from counter import Counter
from helper import Helper

class InjectedComponent:
  def __init__(self, app):
    self._app = app

  def build_node(self, name, idn, input_stream_1, additional_inputs, outputs, output_format):
    self._name = name if name else "component_"+Counter.get()
    self._id = str(idn)
    self._type = "component"
    self._consumes = [input_stream_1]

    if isinstance(additional_inputs, list):
      self._consumes += additional_inputs
    elif additional_inputs != None:
      self._consumes.append(additional_inputs)

    if outputs == None:
      outputs = ["stream_"+Counter.get()]
    elif isinstance(outputs, basestring):
      outputs = [outputs]
    self._emits = outputs

    self._output_format = output_format

    Helper.check_name("component", self._name, self._app._names)
    Helper.check_call_component(self)
    Helper.check_emits("component", self._emits, self._app._streams)

  def run_operation(self):
    print "Embedded components are only instantiated on our cluster, sorry!"
