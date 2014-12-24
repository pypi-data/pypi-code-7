# OPERATION Call Component 
# PYTHON_SYNTAX 
#   stream.call_component( 
#     name = "name",                                           # optional
#     component_id = "component_id_or_name",
#     additional_inputs = [other_input_stream_object_1, ...],  # blank if none
#     outputs = ["output_stream_name_1", ...],                 # optional for single output stream
#     output_format = "replace" OR "merge"                     # optional, defaults to "replace"
#   )
# PYTHON_NOTES 
#  
#  The "component_id" MUST be given and correspond to the id listed in the output of "zillabyte components".
#  
#  The allowed output formats are "replace" and "merge". Note that only linear components, i.e. those with only "each" and "filter" operations support "merge".
#
#    * **"replace"** : discards the input tuple values and only emits the output values. This is the default.
#    * **"merge"** : re-emits the input tuple values along with the output values.
#  
#  To correctly stich in the component, the implicit assumptions below WILL BE USED:
#
#    * The "stream" that "call_component" is invoked on MUST correspond to the first listed input stream to the component.
#    * The streams specified in "additional_inputs" MUST correspond to the other listed input streams in order.
#    * Tuples emitted from the preceeding operation MUST contain the fields listed for the corresponding component input streams.
#    * The streams specified in "outputs" must correspond to the listed output streams to the component in order.
#    * The number of input and output streams specified must match the number listed for the component.
# PYTHON_EXAMPLE 
#  import zillabyte
#  
# dictionary = ["apple", "butterfly", "bus"]
# count = 0
#  
# # next_tuple for source
# def nt(controller):
#   global count
#   global dictionary
#   controller.emit({"word": dictionary[count % len(dictionary)]})
#   count += 1
#  
#   if (count == 5):
#     controller.end_cycle()
#  
#  
# app = zillabyte.app(name="plural_app")
#  
# stream = app.source(name="source", next_tuple=nt, end_cycle_policy="explicit")
# # We call the "pluralize_component" which pluralizes a incoming "word" and outputs it to the "pluralized_words" stream
# stream = stream.call_component(component_id="pluralize", outputs=["pluralized_words"])
#  
# stream.sink(name="plural_words", columns=[{"word":"string"}])
from counter import Counter
from helper import Helper

class InjectedComponent:
  def __init__(self, app):
    self._app = app

  def build_node(self, **kwargs):

    name = kwargs.pop("name", None)
    if name:
      self._name = name 
    else:
      self._name = "component_"+Counter.get()
    self._type = "component"
    self._id = kwargs.pop("component_id", None)

    self._output_format = kwargs.pop("output_format", "replace")

    input_stream_1 = kwargs.pop("input_stream", None)
    if input_stream_1:
      self._consumes = [input_stream_1]
    else:
      self._consumes = []

    additional_inputs = kwargs.pop("additional_inputs", None)
    if isinstance(additional_inputs, list):
      self._consumes += additional_inputs
    elif additional_inputs != None:
      self._consumes.append(additional_inputs)

    outputs = kwargs.pop("outputs", None)
    if outputs == None:
      outputs = ["stream_"+Counter.get()]
    elif isinstance(outputs, basestring):
      outputs = [outputs]
    self._emits = outputs


    Helper.check_name("component", self._name, self._app._names)
    Helper.check_call_component(self)
    Helper.check_emits("component", self._emits, self._app._streams)

  def run_operation(self):
    print "Embedded components are only instantiated on our cluster, sorry!"
