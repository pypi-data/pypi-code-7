import json
from itsdangerous import URLSafeTimedSerializer
from redis import StrictRedis


class Channel(object):
    presence_users_key = 'presence_users:%s'

    def __init__(self, client, channel):
        self.client = client
        self.channel = channel

    def emit(self, event, data, target=None):
        event_data = '%s;%s;%s' % (event, target or "", json.dumps(data))
        self.client.publish(self.channel, event_data)


class EventEmitter(object):
    def __init__(self, client, secret_key='tornadopush'):
        self.client = client
        self.token_serializer = URLSafeTimedSerializer(secret_key)

    def create_token(self, user_id, allowed_channels=None):
        return self.token_serializer.dumps([user_id, allowed_channels])

    def channel(self, name):
        return Channel(self.client, name)

    def emit(self, channel, event, data, target=None):
        self.channel(channel).emit(event, data, target)


_emitter = None

def connect(url=None, secret_key='tornadopush'):
    global _emitter
    if isinstance(url, StrictRedis):
        client = url
    elif url:
        client = StrictRedis.from_url(url)
    else:
        client = StrictRedis()
    _emitter = EventEmitter(client, secret_key)


def emit(channel, event, data, target=None):
    _emitter.emit(channel, event, data, target)