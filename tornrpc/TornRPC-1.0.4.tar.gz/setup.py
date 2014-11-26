from setuptools import setup

description = """
A tornado RPC library.

This RPC framework uses tornado
so its very quick and asynchronous.

This framework supports regular and
asynchronous methods to be registered
with the TornRPCServer. The below example
shows both. The only difference in the
framework is how you register it.
Normal functions are registered using
"server.register()". Async functions
are registered using "server.register_async()".

For more detailed info see the docstring
for TornRPCClient and TornRPCServer.

Example:
### example server code ###

from tornado import gen
from tornrpc.server import TornRPCServer

def test(arg):
  return "You said %s" % arg

@gen.coroutine
def testasync(arg):
  raise gen.Return("You said async %s" % arg)

server = TornRPCServer()
server.register(test)
server.register_async(testasync)
server.start(8080)

### example client code ###

from tornrpc.client import TornRPCClient

client = TornRPCClient('localhost:8080')
client.test('hi')
client.testasync('hi')
"""

setup(
  name='TornRPC',
  version='1.0.4',
  description='A tornado RPC framework',
  long_description=description,
  author='Kyle Laplante',
  author_email='kyle.laplante@gmail.com',
  keywords='rpc tornado asynchronous web',
  packages=['tornrpc', 'tornrpc/client', 'tornrpc/server'],
  install_requires=['tornado'],
)
