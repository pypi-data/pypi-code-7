# coding: utf-8
from __future__ import print_function

from . import pools
from . import messages
from . import id_helper
from . import utils


class RemoteService(object):
    rpc_task_pool = pools.RpcTaskPool(20000, lambda pair: pair[1].cancel(True) if pair and pair[1] else None)


class ServerRemoteService(RemoteService):
    def __init__(self, channel, send_msg_pool):
        self.channel = channel
        self.send_msg_pool = send_msg_pool

    def call_rpc_async(self, service_name, method_name, *method_args):
        msg = messages.RpcMessage(
            id_helper.generate_request_id(), messages.RpcMessage.RPC_EVENT_NAME,
            service_name, method_name, method_args, None, None)
        future = utils.ValueFuture()
        RemoteService.rpc_task_pool.put(msg.request_id, (self.channel, future))
        self.send_msg_pool.offer_message((self.channel, msg))
        return future

    def call_rpc(self, service_name, method_name, *method_args):
        try:
            return self.call_rpc_async(service_name, method_name, *method_args).get()
        except Exception as e:
            return e