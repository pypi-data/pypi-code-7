# coding: utf-8
from __future__ import print_function

import json
from . import utils


class Message(object):
    def to_json(self):
        return json.dumps(self)


class PlainMessage(Message):
    def __init__(self, text):
        self.text = text

    def to_json(self):
        return json.dumps({
            'text': self.text,
        })


class BinaryMessage(Message):
    def __init__(self, bytes):
        self.bytes = bytes


class ExceptionMessage(Message):
    def __init__(self, exception):
        self.exception = exception


class JsonEventMessage(Message):
    def __init__(self, request_id, event_name, data, json):
        self.request_id = request_id
        self.event_name = event_name
        self.data = data
        self.json = json

    def to_json(self):
        return json.dumps({
            'requestId': self.request_id,
            'eventName': self.event_name,
            'data': self.data,
        })


class JsonMessage(Message):
    def __init__(self, json):
        self.json = json

    def to_json(self):
        return json.dumps(self.json)


class RpcMessage(Message):
    RPC_EVENT_NAME = '__rpc__'
    RPC_RESPONSE_EVENT_NAME = '__rpc_response__'

    def __init__(self, request_id, event_name, service_name, method_name, method_args, data, json):
        self.request_id = request_id
        self.event_name = event_name
        self.service_name = service_name
        self.method_name = method_name
        self.method_args = method_args
        self.data = data
        self.json = json

    def to_json(self):
        return json.dumps({
            'requestId': self.request_id,
            'eventName': self.event_name,
            'serviceName': self.service_name,
            'methodName': self.method_name,
            'methodArgs': self.method_args,
            'data': self.data,
        })


class ConnectMessageEvent(object):
    def __init__(self, channel):
        self.channel = channel


class ConnectMessage(Message):
    def __init__(self, channel):
        self.channel = channel


class CloseMessageEvent(object):
    def __init__(self, channel):
        self.channel = channel


class CloseMessage(Message):
    def __init__(self, channel):
        self.channel = channel


class MessageBuilder(object):
    def create_messages(self, channel, data):
        return [(channel, msg) for msg in self.direct_create_messages(data)]

    def direct_create_messages(self, data):
        msgs = []
        if data is None:
            return msgs
        if isinstance(data, CloseMessageEvent):
            msgs.append(CloseMessage(data.channel))
            return msgs
        if isinstance(data, ConnectMessageEvent):
            msgs.append(ConnectMessage(data.channel))
            return msgs
        if isinstance(data, BaseException):
            msgs.append(ExceptionMessage(data))
            return msgs
        if isinstance(data, basestring):
            msgs.append(PlainMessage(data))
            json_data = utils.try_parse_json(data)
            if json_data is None:
                return msgs
            msgs.append(JsonMessage(json_data))
            if json_data.get('requestId') and json_data.get('eventName'):
                request_id = json_data.get('requestId')
                event_name = json_data.get('eventName')
                data = json_data.get('data')
                msgs.append(JsonEventMessage(request_id, event_name, data, json_data))
                if RpcMessage.RPC_EVENT_NAME == event_name or RpcMessage.RPC_RESPONSE_EVENT_NAME == event_name:
                    service_name = json_data.get('serviceName')
                    method_name = json_data.get('methodName')
                    method_args = json_data.get('methodArgs')
                    if method_args is None:
                        method_args = []
                    msgs.append(
                        RpcMessage(request_id, event_name, service_name, method_name, method_args, data, json_data))
        # TODO: create binary type messages
        return msgs

