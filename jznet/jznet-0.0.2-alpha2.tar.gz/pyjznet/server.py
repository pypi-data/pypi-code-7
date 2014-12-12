# coding: utf-8
from __future__ import print_function
from geventwebsocket import WebSocketServer, WebSocketApplication, Resource
import sys
import logging
from . import pools
from . import processors
from . import listeners
from . import messages

root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


class Server(object):
    def __init__(self):
        self.rpc_services = []
        self._send_msg_pool = pools.SendMessagePool()
        self._receive_msg_pool = pools.ReceiveMessagePool()
        self.message_builder = messages.MessageBuilder()

    def add_rpc_service(self, name, rpc_service):
        self.rpc_services.append((name, rpc_service))

    def start(self, host='127.0.0.1', port=8000):
        send_msg_pool = self._send_msg_pool
        receive_msg_pool = self._receive_msg_pool
        message_builder = self.message_builder
        send_msg_pool.add_listener(object, listeners.SendMessageHandler())

        class WSApplication(WebSocketApplication):
            def on_open(self, ):
                print("Connection opened")

            def on_close(self, reason):
                print('Connection closed')

            def on_message(self, message):
                print('got message', message)
                receive_msg_pool.offer_messages(message_builder.create_messages(self, message))
                # self.ws.send(message)

        msg_processor = processors.MessageProcessor(receive_msg_pool, send_msg_pool)
        msg_processor.add_rpc_services(self.rpc_services)
        msg_processor.start()
        ws_server = WebSocketServer(
            (host, port),
            Resource({'/': WSApplication,
                      '/websocket': WSApplication})
        )
        print("start to listen at http://%s:%d" % (host, port))
        ws_server.serve_forever()