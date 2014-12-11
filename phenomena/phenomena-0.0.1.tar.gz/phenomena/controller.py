import json

from ontic import ontic_type
import zmq.green as zmq

from command_message import CommandMessage
import string_to_ontic


class Controller(object):
    def __init__(self, event_core, port):
        """

        :param event_core:
        :type event_core: event_core.EventCore
        :param log:
        :type log: logging
        :param port:
        :type port: int
        :return: A valid Controller
        :rtype: Controller
        """
        self.event_core = event_core
        self.log = event_core.log
        self.port = port

        # configure sockets
        self._listener = self.event_core._zmq_ctx.socket(zmq.SUB)
        self._listener.setsockopt(zmq.SUBSCRIBE, '')
        self._listener.bind('tcp://*:%s' % self.port)
        self._sender = self.event_core._zmq_ctx.socket(zmq.PUB)
        self._sender.connect('tcp://localhost:%s' % self.port)

    @property
    def listener(self):
        return self._listener

    def handle_msg(self):
        """
        """
        msg = self._listener.recv()
        self.log.debug('handle_msg: "%s"', msg)

        if not msg:
            self.log.error('Empty message delivered.')
            return

        cmd_load = json.loads(msg)
        self.log.debug('cmd_load: %s', cmd_load)
        if not cmd_load:
            self.log.error('Empty command message delivered.')
            return

        # todo: raul - this is where I need a string to model converter
        cmd_msg = string_to_ontic.transform(CommandMessage, cmd_load)
        ontic_type.validate_object(cmd_msg)

        if cmd_msg.cmd == CommandMessage.CMD_KILL:
            self.log.info('Received kill message.')
            self.event_core._stopped = True
            return

    def signal_message(self, msg):
        """

        :param msg:
        :type msg: dict
        :return:
        """
        self._sender.send(json.dumps(msg))

    def close_connections(self):
        self._sender.close()
        self._listener.close()
