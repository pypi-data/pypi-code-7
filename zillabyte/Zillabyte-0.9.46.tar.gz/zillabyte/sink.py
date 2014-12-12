# OPERATION Sink 
# PYTHON_SYNTAX  
#   stream.sink( 
#     name = "relation_name",
#     columns = [{"field_1" : "type_1"}, {"field_2" : "type_2"}, ...]
#   )
# PYTHON_NOTES 
# "Sink" relation "name" must be specified as a non-empty STRING with only alphanumeric and underscore characters!
#  
# "Columns" must be a non-empty LIST.
#  
# Field names must be non-empty STRINGS with only alphanumeric or underscore characters.
#  
# Field names cannot be "v[number]", "id", "confidence", "since" or "source" which are reserved Zillabyte names.
#  
# Field types may be "string", "integer", "float", "double", "boolean", "array" or "map".
# PYTHON_EXAMPLE 
# stream.sink(name = "test_python_sink", columns = [{"url":"string"},{"title":"string"}])
from helper import Helper

class Sink:
  def __init__(self, app):
    self._app = app

  def build_node(self, **kwargs):
    self._name = kwargs.get("name", None)
    self._type = "sink"
    self._columns =  kwargs.get("columns", None)
    self._relation = kwargs.get("relation", self._name)
    self._scope = kwargs.get("scope", None)

    Helper.check_sink(self._name, self._columns, self._app._nodes, "sink")

  def run_operation(self):
    print "Sinks cannot be run!"
