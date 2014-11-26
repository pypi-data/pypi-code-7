from tornado import gen, log, web

class _Handler(web.RequestHandler):
  __ALLOWEDUA__ = ('TornRPCClient')

  @gen.coroutine
  def initialize(self):
    self.log = log.logging.getLogger()
    self.log.setLevel(log.logging.INFO)

  @gen.coroutine
  def prepare(self):
    ua = self.request.headers.get('User-Agent')
    if ua not in self.__ALLOWEDUA__:
      self.log.info('Received request from UA {0}'.format(ua))
      self.write({'error': 'User agent not allowed: {0}'.format(ua)})
      self.finish()

  @gen.coroutine
  def args_kwargs(self):
    args = []
    # support positional arguments
    if '__args' in self.request.arguments:
      args = self.request.arguments['__args']
      del self.request.arguments['__args']
    # keyword arguments get passed as a list so extract them
    kwargs = dict([(k, v[0]) for k, v in self.request.arguments.items()])
    raise gen.Return((args, kwargs))

class _Base(_Handler):
  """
  Class to make a route for getting the result from
  synchronous RPC functions
  """

  TYPE = 'synchronous'

  @gen.coroutine
  def get(self):
    args, kwargs = yield self.args_kwargs()
    try:
      # return JSON so we get the correct type of the return value
      self.write({'response': self.func[0](*args, **kwargs)})
    except Exception as e:
      self.write({'error': str(e)})

class _AsyncBase(_Handler):
  """
  Class to make a route for getting the result from
  asynchronous RPC functions
  """

  TYPE = 'asynchronous'

  @gen.coroutine
  def get(self):
    args, kwargs = yield self.args_kwargs()
    try:
      ret = yield self.func[0](*args, **kwargs)
      # return JSON so we get the correct type of the return value
      self.write({'response': ret})
    except Exception as e:
      self.write({'error': str(e)})
