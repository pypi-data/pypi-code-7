# coding: utf-8
from __future__ import print_function
import logging

from . import messages
from . import services


class PoolListener(object):
    def watch_pool(self, pool, key_type):
        pool.add_listener(key_type, self)

    def on_message(self, msg):
        pass

    def create_process_message_task(self, msg):
        return lambda: self.on_message(msg)


class MessageHandler(PoolListener):
    def __init__(self):
        self._send_msg_pool = None

    @property
    def send_msg_pool(self):
        return self._send_msg_pool

    def interest(self):
        pass

    def listen(self, pool):
        self.watch_pool(pool, self.interest())
        return self

    def process(self, channel, msg):
        pass

    def on_message(self, msg):
        self.process(msg[0], msg[1])


class SimpleMessageHandler(MessageHandler):
    def __init__(self, pool):
        MessageHandler.__init__(self)
        self._send_msg_pool = pool


class PlainMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.PlainMessage

    def process(self, channel, msg):
        logging.info("got plain message %s" % str(msg.to_json()))


class BinaryMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.BinaryMessage

    def process(self, channel, msg):
        print("got binary message", msg)


class CloseMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.CloseMessage

    def process(self, channel, msg):
        print("got close message")


class ExceptionMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.ExceptionMessage

    def process(self, channel, msg):
        print('got exception message', msg)


class ConnectMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.ConnectMessage

    def process(self, channel, msg):
        print('got connect msg', msg)


class JsonMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.JsonMessage

    def process(self, channel, msg):
        logging.info('got json message %s' % str(msg.to_json()))


class JsonEventMessageHandler(SimpleMessageHandler):
    def interest(self):
        return messages.JsonEventMessage

    def process(self, channel, msg):
        logging.info('got json event message %s' % str(msg.to_json()))


class SendMessageHandler(PoolListener):
    def __init__(self):
        PoolListener.__init__(self)

    def on_message(self, msg):
        print('need to send msg', msg)
        channel = msg[0]
        msg = msg[1]
        if isinstance(msg, messages.CloseMessage) or isinstance(msg, messages.ExceptionMessage):
            channel.ws.close()
        elif isinstance(msg, messages.PlainMessage) or isinstance(msg, messages.JsonMessage) \
                or isinstance(msg, messages.JsonEventMessage) or isinstance(msg, messages.RpcMessage):
            channel.ws.send(msg.to_json())
        else:
            pass  # TODO: binary message send


class RpcMessageHandler(SimpleMessageHandler):
    def __init__(self, pool):
        SimpleMessageHandler.__init__(self, pool)
        self._rpc_services = {}

    def add_rpc_service(self, name, rpc_service):
        self._rpc_services[name] = rpc_service

    def add_rpc_services(self, pairs):
        for pair in pairs:
            self.add_rpc_service(pair[0], pair[1])

    def interest(self):
        return messages.RpcMessage

    def process(self, channel, msg):
        logging.info('got rpc message %s' % str(msg.to_json()))
        try:
            event_name = msg.event_name
            if messages.RpcMessage.RPC_EVENT_NAME == event_name:
                self._process_rpc_request(channel, msg)
            elif messages.RpcMessage.RPC_RESPONSE_EVENT_NAME == event_name:
                self._process_rpc_response(channel, msg)
        except Exception as e:
            logging.error(e)

    def _find_method_of_rpc_service(self, rpc_service, method_name):
        methods = dir(rpc_service)
        for name in methods:
            method = getattr(rpc_service, name)
            if name == method_name:
                return method
                # attr_name = '__rpc_method_name_%s' % name
                # attr_val = getattr(rpc_service, attr_name)
                # if attr_val is not None:
                # if attr_val == method_name:
                # return method
        return None

    def _process_rpc_request(self, channel, msg):
        if channel is None or msg is None:
            return
        service_name = msg.service_name
        method_name = msg.method_name
        method_args = msg.method_args
        rpc_service = self._rpc_services.get(service_name)
        if rpc_service is None:
            logging.info("Can't find rpc service %s/%s" % (service_name, method_name))
            return
        method = self._find_method_of_rpc_service(rpc_service, method_name)
        if method is None:
            logging.info("Can't find rpc service %s/%s" % (service_name, method_name))
            return
        try:
            kwargs = {
                'remote_service': services.ServerRemoteService(channel, self.send_msg_pool)
            }
            res = method(*method_args, **kwargs)
        except TypeError as e:
            res = method(*method_args)
        msg = messages.RpcMessage(msg.request_id, messages.RpcMessage.RPC_RESPONSE_EVENT_NAME,
                                  service_name, method_name, None, res, None)
        self._send_msg_pool.offer_message((channel, msg))

    def _process_rpc_response(self, channel, msg):
        if channel is None or msg is None:
            return
        task_pair = services.RemoteService.rpc_task_pool.get(msg.request_id)
        if task_pair is None or task_pair[1] is None:
            logging.info("Can't find the request for this response: %s" % msg.request_id)
            return
        future = task_pair[1]
        future.set_result(msg.data)
