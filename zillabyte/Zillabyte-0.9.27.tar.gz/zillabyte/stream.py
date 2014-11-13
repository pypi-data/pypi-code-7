from helper import Helper
from operation_handler import OperationHandler

class Stream:
  def __init__(self, name, app, previous_node_name):
    self._name = name
    self._app = app
    self._previous_node_name = previous_node_name

  def each(self, name=None, emits=None, output_format="replace", prepare=None, execute=None, parallelism=None):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_multilang_operation("each", name, emits, output_format, prepare, execute, parallelism)\
                 .add_operation_properties_to_info("name", "type", "output_format")\
                 .add_optional_operation_properties_to_info("parallelism")\
                 .create_arc_info_from_stream(self)\
                 .handle_operation()\
                 .get_output_streams()
    return streams

  def filter(self, name=None, emits=None, prepare=None, keep=None, parallelism=None):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_multilang_operation("filter", name, emits, prepare, keep, parallelism)\
                .add_operation_properties_to_info("name", "type")\
                .add_optional_operation_properties_to_info("parallelism")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def group_by(self, name=None, emits=None, fields=None, prepare=None, begin_group=None, aggregate=None, end_group=None, parallelism=None):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_multilang_operation("group_by", name, emits, fields, prepare, begin_group, aggregate, end_group, parallelism)\
                .add_operation_properties_to_info("name", "type", "group_by")\
                .add_optional_operation_properties_to_info("parallelism")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def join_with(self, name=None, stream=None, emits=None, fields=None, options=None):
    lhs_stream = self
    rhs_stream = stream
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_multilang_operation("join", name, self, stream, emits, fields, options)\
                .add_operation_properties_to_info("name", "type", "lhs_stream", "rhs_stream", "lhs_fields", "rhs_fields", "join_type")\
                .create_arc_info_from_stream(lhs_stream, "left")\
                .create_arc_info_from_stream(rhs_stream, "right")\
                .handle_operation()\
                .get_output_streams()
    return streams

  def call_component(self, name=None, component_id=None, additional_inputs=None, outputs=None, output_format="replace"):
    op = OperationHandler(self._app, self.__class__)
    op = op.build_multilang_operation("component", name, component_id, self, additional_inputs, outputs, output_format)\
           .add_operation_properties_to_info("name", "type", "id", "output_format")
    node = op.node()
    for stream in node._consumes:
      op = op.create_arc_info_from_stream(stream)
    streams = op.handle_operation()\
                .get_output_streams()
    return streams

  def loop_back(self, operation, max_iterations=None):
    Helper.check_loop_back(self, operation, max_iterations, self._app._nodes)
    arc_hash = {"name" : self._name, "origin" : self._previous_node_name, "dest" : operation, "loop_back" : 1}
    if max_iterations != None:
      arc_hash["max_iterations"] = max_iterations
    Helper.write_arc_to_file(arc_hash, self._app._socket)
    return self

  def sink(self, name=None, columns=None, relation=None, scope=None):
    op = OperationHandler(self._app, self.__class__)
    op.build_multilang_operation("sink", name, columns, relation, scope)\
      .add_operation_properties_to_info("name", "type", "columns", "relation", "scope")\
      .create_arc_info_from_stream(self)\
      .handle_operation()

  def unique(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("unique", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("group_fields")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def count(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("count", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("group_fields")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def remove(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("remove", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("remove")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def retain(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("retain", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("retain")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def clump(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("clump", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("clump")\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams

  def rename(self, *args):
    op = OperationHandler(self._app, self.__class__)
    streams = op.build_jvm_operation("rename", *args)\
                .add_operation_properties_to_info("name", "type")\
                .add_input_args_to_info_as("rename", 0)\
                .create_arc_info_from_stream(self)\
                .handle_operation()\
                .get_output_streams()
    return streams
