from controller import *
from stream import Stream
from operation_handler import OperationHandler
from helper import Helper
from base import Base
from version import VERSION

class App(Base):
  def __init__(self, name=None):
    Base.__init__(self, name)
    Helper.check_name("app", self._name, {})
    self._options = Helper.opt_parser()

    if(self._options["command"] == "info"):
      sock = None
      if (self._options["host"] is not None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._options["host"], int(self._options["port"])))
      elif (self._options["unix_socket"] is not None):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.connect(self._options["unix_socket"])
      self._socket = sock.makefile()
      Helper.write_hash_to_file({"language":"python", "name":self._name, "flow_type":"app", "multilang_version":VERSION}, self._socket)

  def source(self, name=None, matches=None, options={}, emits=None, end_cycle_policy="null_emit", prepare=None, begin_cycle=None, next_tuple=None):
    op = OperationHandler(self, Stream)
    streams = op.build_multilang_operation("source", name, matches, options, emits, end_cycle_policy, prepare, begin_cycle, next_tuple)\
                       .add_operation_properties_to_info("name", "type")\
                       .add_optional_operation_properties_to_info("relation", "matches", "end_cycle_policy")\
                       .handle_operation()\
                       .get_output_streams()
    return streams

  def call_component(self, name=None, component_id=None, outputs=None, output_format="replace"):
    op = OperationHandler(self, Stream)
    op = op.build_multilang_operation("component", name, component_id, self, None, outputs, output_format)\
           .add_operation_properties_to_info("name", "type", "id", "output_format")
    node = op.node()
    streams = op.handle_operation()\
                .get_output_streams()
    return streams
