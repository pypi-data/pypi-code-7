import json
import requests
from urlparse import urljoin

class _RPC(object):
  __HEADERS__ = {'User-Agent': 'TornRPCClient'}
  def __init__(self, server, name):
    self._name = name
    self._url = urljoin(server, name)

  def __call__(self, *args, **kwargs):
    if args:
      # the server will turn this list into
      # positional args
      kwargs['__args'] = args

    try:
      resp = requests.get(self._url, data=kwargs, headers=self.__HEADERS__)
    except Exception as e:
      raise TornRPCClient.FailedCall(e)

    if resp.status_code == 404:
      raise TornRPCClient.MissingMethod(
          'No remote method found for {0}'.format(self._name))

    try:
      ret = json.loads(resp.content)
    except Exception as e:
      raise TornRPCClient.InvalidSerializationError(e)

    if 'error' in ret:
      raise TornRPCClient.FailedCall(ret['error'])

    return ret['response']

class TornRPCClient(object):
  """
  Client for talking to TornRPCServer servers.

  Example:
    from tornrpc.client import TornRPCClient
    client = TornRPCClient('http://myserver.com:9091')

    # If you want to include some methods that are not allowed
    # to be called include them in the unallowed_methods argument
    # to the constructor. If you do not want auto-completion or dir
    # fulfillment use load_remotes=False in the constructor.

    # then just call any remote method on your client
    client.remote_method_name(args)
  """

  class FailedCall(Exception): pass
  class InvalidSerializationError(Exception): pass
  class MissingMethod(Exception): pass

  __UNALLOWED__ = [
    # iPython calls these when using tab-complete.
    # dont allow these methods to be sent to the
    # server since _loadremotemethods() takes care
    # of tab-completion.
    'trait_names',
    '_getAttributeNames',
  ]

  def __init__(self, server, unallowed_calls=[], load_remotes=True):
    if server.startswith('http'):
      self._server = server
    else:
      self._server = 'http://{0}'.format(server)
    self._unallowed = unallowed_calls + self.__UNALLOWED__
    if load_remotes:
      self.__loadremoteroutes()

  def __send(self, name):
    return _RPC(self._server, name)

  def __remoteroutes(self):
    return self._getroutes()

  def __loadremoteroutes(self):
    for route in self.__remoteroutes():
      setattr(self, route, self.__send(route))

  def __getattr__(self, name):
    return None if name in self._unallowed else self.__send(name)


__all__ = ('TornRPCClient')
