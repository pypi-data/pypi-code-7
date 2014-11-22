# OPERATION Component Input
# PYTHON_SYNTAX 
#   component.inputs( 
#     name = "input_stream_name",
#     fields = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] 
#   )
# PYTHON_NOTES 
#   "Inputs" stream "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
#  
#   "Fields" must be a non-empty LIST.
#  
#   Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
#  
#   Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
#  
#   Field types may be "string", "integer", "float", "double", "boolean", "array" or "map".
# PYTHON_EXAMPLE 
# import zillabyte 
#  
# component = zillabyte.component("python_component")
#  
#  # We declare the input stream with a schema containing the "word" field
# stream = component.inputs(name = "input_stream", fields = [{"word" : "string"}])
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
