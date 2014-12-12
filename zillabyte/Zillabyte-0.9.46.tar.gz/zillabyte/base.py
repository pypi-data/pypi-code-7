from operation_handler import OperationHandler

class Base:
  def __init__(self, name):
    self._nodes = []
    self._streams = {}
    self._names = {}
    self._name = name

  def _source_common(self, stream_class, *args, **kwargs):

    op = OperationHandler(self, stream_class)
    streams = op.build_multilang_operation("source", *args, **kwargs)\
                       .add_operation_properties_to_info("name", "type")\
                       .add_optional_operation_properties_to_info("relation", "matches", "end_cycle_policy")\
                       .handle_operation()\
                       .get_output_streams()
    return streams

  def _call_component_common(self, input_stream, output_stream_class, *args, **kwargs):
    if len(args) == 1:
      kwargs["component_id"] = args[0]
    kwargs["input_stream"] = input_stream

    op = OperationHandler(self, output_stream_class)
    op = op.build_multilang_operation("component", **kwargs)\
           .add_operation_properties_to_info("name", "type", "id", "output_format")

    node = op.node()
    if not node._consumes[0] == None:
      for stream in node._consumes:
        op = op.create_arc_info_from_stream(stream)
    streams = op.handle_operation()\
                .get_output_streams()
    return streams
