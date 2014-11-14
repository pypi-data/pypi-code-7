from stream import Stream
from operation_handler import OperationHandler

class ComponentStream(Stream):
  def sink(self, name=None, fields=None):
    self.outputs(name, fields)

  def outputs(self, name=None, fields=None, relation=None, scope=None):
    op = OperationHandler(self._app, self.__class__)
    op.build_multilang_operation("component_output", name, fields, relation, scope)\
      .add_operation_properties_to_info("name", "type", "columns", "relation", "scope")\
      .create_arc_info_from_stream(self)\
      .handle_operation()
