from stream import Stream
from operation_handler import OperationHandler

class ComponentStream(Stream):
  def sink(self, **kwargs):
    self.outputs(**kwargs)

  def outputs(self, **kwargs):

    op = OperationHandler(self._app, self.__class__)
    op.build_multilang_operation("component_output", **kwargs)\
      .add_operation_properties_to_info("name", "type", "columns", "relation", "scope")\
      .create_arc_info_from_stream(self)\
      .handle_operation()
