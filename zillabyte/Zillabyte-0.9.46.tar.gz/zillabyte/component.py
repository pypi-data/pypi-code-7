from controller import *
from counter import Counter
from helper import Helper
from component_stream import ComponentStream
from operation_handler import OperationHandler
from base import Base
from version import VERSION

class Component(Base):
  def __init__(self, name=None):
    Base.__init__(self, name)
    Helper.check_name("component", self._name, {})
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
      Helper.write_hash_to_file({"language":"python", "name":self._name, "flow_type":"component", "multilang_version":VERSION}, self._socket)

  def inputs(self, **kwargs):
    op = OperationHandler(self, ComponentStream)

    streams = op.build_multilang_operation("component_input", **kwargs)\
                .add_operation_properties_to_info("name", "type", "fields")\
                .handle_operation()\
                .get_output_streams()
    return streams

  def source(self, name=None, matches=None, options={}, emits=None, end_cycle_policy="null_emit", prepare=None, begin_cycle=None, next_tuple=None):
    return Base._source_common(self, ComponentStream, name, matches, options, emits, end_cycle_policy, prepare, begin_cycle, next_tuple)
