###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License, version 3,
##  as published by the Free Software Foundation.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################


from __future__ import absolute_import

__all__ = ['create_guest_worker_client_factory']

import json

from twisted.python import log
from twisted.internet import protocol
from twisted.internet.error import ProcessDone, \
                                   ProcessTerminated, \
                                   ProcessExitedAlready, \
                                   ConnectionDone, \
                                   ConnectionClosed, \
                                   ConnectionLost, \
                                   ConnectionAborted



class GuestWorkerClientProtocol(protocol.Protocol):

   def __init__(self, config, debug = False):
      self.config = config
      self.debug = debug


   def connectionMade(self):
      ## `self.transport` is now a provider of `twisted.internet.interfaces.IProcessTransport`
      ## see: http://twistedmatrix.com/documents/current/api/twisted.internet.interfaces.IProcessTransport.html

      options = self.config.get('options', {})

      if self.debug:
         log.msg("GuestWorkerClientProtocol.connectionMade")

      if 'stdout' in options and options['stdout'] == 'close':
         self.transport.closeStdout()
         if self.debug:
            log.msg("GuestWorkerClientProtocol: stdout to guest closed")

      if 'stderr' in options and options['stderr'] == 'close':
         self.transport.closeStderr()
         if self.debug:
            log.msg("GuestWorkerClientProtocol: stderr to guest closed")

      if 'stdin' in options:
         if options['stdin'] == 'close':
            self.transport.closeStdin()
            if self.debug:
               log.msg("GuestWorkerClientProtocol: stdin to guest closed")
         else:
            if options['stdin']['type'] == 'json':

               self.transport.write(json.dumps(options['stdin']['value']))
               if self.debug:
                  log.msg("GuestWorkerClientProtocol: JSON value written to stdin on guest")

            elif options['stdin']['type'] == 'msgpack':
               raise Exception("not implemented")

            else:
               raise Exception("logic error")

            if options['stdin'].get('close', True):
               self.transport.closeStdin()
               if self.debug:
                  log.msg("GuestWorkerClientProtocol: stdin to guest closed")

      self.factory._on_ready.callback(self)



   def connectionLost(self, reason):
      if self.debug:
         log.msg("GuestWorkerClientProtocol.connectionLost: {}".format(reason))
      try:
         if isinstance(reason.value,  ProcessDone):
            if self.debug:
               log.msg("GuestWorkerClientProtocol: guest ended cleanly")
            self.factory._on_exit.callback(None)

         elif isinstance(reason.value, ProcessTerminated):
            if self.debug:
               log.msg("GuestWorkerClientProtocol: guest ended with error {}".format(reason.value.exitCode))
            self.factory._on_exit.errback(reason)

         else:
            ## should not arrive here
            log.msg("GuestWorkerClientProtocol: INTERNAL ERROR - should not arrive here")
      except Exception as e:
         log.msg("GuestWorkerClientProtocol: INTERNAL ERROR - {}".format(e))


   def signal(self, sig = 'TERM'):
      assert(sig in ['KILL', 'TERM', 'INT'])
      try:
         self.transport.signalProcess(sig)
      except ProcessExitedAlready:
         pass
      except OSError as e:
         log.msg(e)



class GuestWorkerClientFactory(protocol.Factory):

   def __init__(self, config, on_ready, on_exit, debug = True):
      self.debug = debug
      self.proto = None
      self._config = config
      self._on_ready = on_ready
      self._on_exit = on_exit

   def buildProtocol(self, addr):
      self.proto = GuestWorkerClientProtocol(self._config, debug = self.debug)
      self.proto.factory = self
      return self.proto

   def signal(self, sig = 'TERM'):
      assert(sig in ['KILL', 'TERM', 'INT'])
      if self.proto:
         self.proto.signal(sig)



def create_guest_worker_client_factory(config, on_ready, on_exit):
   factory = GuestWorkerClientFactory(config, on_ready, on_exit)
   return factory
