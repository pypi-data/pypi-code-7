from operation_handler import OperationHandler

class Base:
  def __init__(self, name):
    self._nodes = []
    self._streams = {}
    self._names = {}
    self._name = name

  def _source_common(self, stream_class, name=None, matches=None, options={}, emits=None, end_cycle_policy="null_emit", prepare=None, begin_cycle=None, next_tuple=None):
    op = OperationHandler(self, stream_class)
    streams = op.build_multilang_operation("source", name, matches, options, emits, end_cycle_policy, prepare, begin_cycle, next_tuple)\
                       .add_operation_properties_to_info("name", "type")\
                       .add_optional_operation_properties_to_info("relation", "matches", "end_cycle_policy")\
                       .handle_operation()\
                       .get_output_streams()
    return streams

  def _call_component_common(self, input_stream, output_stream_class, *args, **kwargs):
    name = kwargs.get("name", None)
    component_id = args[0] if len(args) == 1 else kwargs.get("component_id", None)
    additional_inputs = kwargs.get("additional_inputs", None)
    outputs = kwargs.get("outputs", None)
    output_format = kwargs.get("output_format", "replace")

    op = OperationHandler(self, output_stream_class)
    op = op.build_multilang_operation("component", name, component_id, input_stream, additional_inputs, outputs, output_format)\
           .add_operation_properties_to_info("name", "type", "id", "output_format")
    node = op.node()
    if not node._consumes[0] == None:
      for stream in node._consumes:
        op = op.create_arc_info_from_stream(stream)
    streams = op.handle_operation()\
                .get_output_streams()
    return streams
