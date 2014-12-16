from controller import *
from stream import Stream
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

  def source(self, *args, **kwargs):
    return Base._source_common(self, Stream, *args, **kwargs)

  def call_component(self, *args, **kwargs):
    return Base._call_component_common(self, None, Stream, *args, **kwargs)
