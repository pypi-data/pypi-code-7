from controller import *
from helper import Helper
from source import Source
from each import Each
from filter import Filter
from group_by import GroupBy
from join import Join
from injected_component import InjectedComponent
from sink import Sink
from component_input import ComponentInput
from component_output import ComponentOutput
from jvm_operation import JvmOperation

class OperationHandler:

  def __init__(self, app, stream_class):
    self._app = app
    self._stream_class = stream_class
    self._node_hash_pars = []
    self._node_hash_optpars = []
    self._node_hash_elements = {}
    self._arc_hash_streams = {}

  def node(self):
    return self._node

  def build_multilang_operation(self, op_type, *args, **kwargs):
    if op_type == "source":
      self._node = Source(self._app)
    elif op_type == "each":
      self._node = Each(self._app)
    elif op_type == "filter":
      self._node = Filter(self._app)
    elif op_type == "group_by":
      self._node = GroupBy(self._app)
    elif op_type == "join":
      self._node = Join(self._app)
    elif op_type == "component":
      self._node = InjectedComponent(self._app)
    elif op_type == "sink":
      self._node = Sink(self._app)
    elif op_type == "component_input":
      self._node = ComponentInput(self._app)
    elif op_type == "component_output":
      self._node = ComponentOutput(self._app)
    else:
      raise "unknown type"

    # kwargs
    self._node.build_node(*args, **kwargs)
    return self

  def build_jvm_operation(self, op_type, *args):
    self._node = JvmOperation(op_type)
    self._node.build_node(*args)
    return self

  def add_operation_properties_to_info(self, *args):
    self._node_hash_pars += args
    return self

  def add_optional_operation_properties_to_info(self, *args):
    self._node_hash_optpars += args
    return self

  def add_input_args_to_info_as(self, key, index=None):
    if index == None:
      self._node_hash_elements[key] = self._node._args
    else:
      self._node_hash_elements[key] = self._node._args[index]
    return self

  def create_arc_info_from_stream(self, stream, direction=None):
    self._arc_hash_streams[stream] = direction
    return self

  def handle_operation(self):
    self._app._nodes.append(self._node)

    if(self._app._options["command"] == "info"):
      node_hash = self._node_hash_elements
      # Add parameters from operation
      for par in self._node_hash_pars:
        node_hash[par] = eval("self._node._"+par)
      # Add optional parameters from operation
      for par in self._node_hash_optpars:
        if eval("self._node._"+par) != None:
          node_hash[par] = eval("self._node._"+par)
      # Always add options if they are not null
      if hasattr(self._node, "_options"):
        node_hash["config"] = self._node._options
      Helper.write_node_to_file(node_hash, self._app._socket)

      for stream in self._arc_hash_streams:
        arc_hash = {"name":stream._name, "origin":stream._previous_node_name, "dest":self._node._name}
        direction = self._arc_hash_streams[stream]
        if direction != None:
          arc_hash[direction] = 1
        Helper.write_arc_to_file(arc_hash, self._app._socket)

    elif self._app._options["command"] == "execute" and self._app._options["name"] == self._node._name:
      self._node.run_operation()

    return self

  def get_output_streams(self):
    output_streams = []
    for stream in self._node._emits:
      output_streams.append(self._stream_class(stream, self._app, self._node._name))
    if len(output_streams) == 1:
      output_streams = output_streams[0]

    return output_streams
