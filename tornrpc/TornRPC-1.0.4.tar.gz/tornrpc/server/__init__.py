from tornado import (
    gen,
    ioloop,
    log,
    web
)

from .handlers import _AsyncBase, _Base

class TornRPCServer(object):
  """
  Server for TornRPC.

  Example:
    from tornrpc.server import TornRPCServer
    server = TornRPCServer()

    # create your functions and register them
    # to the server.
    # you dont need to use async funcs
    # but it is recommended.
    # Here is an example that uses both asycn
    # and non-async

    def not_async(arg=None):
      return arg

    @gen.coroutine
    def is_async(arg=None):
      raise gen.Return(arg)

    server.register(not_async)
    server.register_async(is_async)    

    # start the server on the desired port
    port = 8080
    server.start(port)

  Use the TornRPCClient to talk to this server
  """

  def __init__(self):
    self._routes = []
    self.log = log.logging.getLogger()
    self.log.setLevel(log.logging.INFO)
    log.enable_pretty_logging(logger=self.log)
    self.register_async(self._getroutes)

  @gen.coroutine
  def _getroutes(self):
    # this is support for the client to have a list
    # of all the remote methods
    raise gen.Return([v.__name__ for _, v in self._routes])

  def _make(self, func, base):
    name = func.__name__
    # put func into a list as the only item because if
    # we assign it as a method it will be required to have
    # self as the first arg and we dont want that
    handler = type(name, (base,), {'func': [func]})
    self._routes.append((r'/{0}'.format(name), handler))
    self.log.info('Registered {0} command {1}'.format(base.TYPE, name))

  def register(self, func):
    """
    Register normal synchronous functions.
    Use this to register functions
    that do NOT return Futures.

    Just pass the function name:
      def test():
        return True
      register(test)
    """

    self._make(func, _Base)

  def register_async(self, func):
    """
    Register an asynchronous function.
    Use this to register functions that
    DO return Futures. Generally these
    functions will be wrapped in
    @gen.coroutine.

    Just pass the function name:
      @gen.coroutine
      def test():
        raise gen.Return(True)
    """

    self._make(func, _AsyncBase)

  def start(self, port):
    """
    Start a TornRPCServer on the defined port
    """

    self.log.info('Starting server on port {0}'.format(port))
    app = web.Application(self._routes, debug=True)
    app.listen(int(port))
    ioloop.IOLoop.current().start()


__all__ = ('TornRPCServer')
