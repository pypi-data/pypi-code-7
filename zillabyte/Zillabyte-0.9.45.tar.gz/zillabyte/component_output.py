# OPERATION Component Output
# PYTHON_SYNTAX 
#   component_stream.outputs( 
#     name = "output_stream_name",
#     fields = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...] 
#   )
# PYTHON_NOTES 
#   "Outputs" stream "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
#  
#   "Fields" must be a non-empty LIST.
#  
#   Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
#  
#   Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
#  
#   Field types may be "string", "integer", "float", "double", "boolean", "array" or "map".
# PYTHON_EXAMPLE 
# stream.outputs(name = "output_stream", fields = [{"word" : "string"}])
from helper import Helper

class ComponentOutput:
  def __init__(self, app):
    self._app = app

  def build_node(self, **kwargs):

    self._name = kwargs.get("name")
    self._type = "output"
    self._columns = kwargs.get("fields")
    
    relation = kwargs.get("relation")
    if relation != None:
      self._relation = relation
    else:
      self._relation = self._name
    self._scope = kwargs.get("scope")

    Helper.check_sink(self._name, self._columns, self._app._nodes, "outputs")

  def run_operation(self):
    print "Component sinks cannot be run!"
