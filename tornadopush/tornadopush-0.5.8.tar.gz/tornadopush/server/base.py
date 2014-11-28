import logging
from itsdangerous import BadSignature
from tornado import ioloop, websocket
import datetime
import uuid


logger = logging.getLogger('tornadopush')


class ChannelMixin(object):
    @property
    def channel(self):
        return getattr(self, '_channel', None)

    @channel.setter
    def channel(self, channel):
        if not channel:
            channel = self.application.settings['default_channel']
        allowed_channels = self.application.settings['allowed_channels']
        if allowed_channels and channel not in allowed_channels:
            self.send_error(404)
        self._channel = channel

    @property
    def channel_key(self):
        return self.application.settings['channel_format'] % self.channel


class AuthentifyMixin(object):
    @property
    def auth_enabled(self):
        return self.application.settings['auth_enabled']

    def authentify(self, token=None, callback=None):
        self.user_id = None
        self.user_channels = None
        if not callback:
            callback = self.on_authorized
        if token:
            self._validate_token(token)
        if self.user_id is None and self.auth_enabled:
            logger.debug('Token %s rejected' % token)
            self.on_unauthorized()
        else:
            if self.user_id:
                logger.debug('User %s connected on #%s' % (self.user_id, self.channel))
            else:
                logger.debug('New anonymous connected on #%s' % self.channel)
                self.user_id = str(uuid.uuid4())
            callback()

    def _validate_token(self, token):
        max_age = self.application.settings['token_max_age']
        try:
            user_id, user_channels = self.application.token_serializer.loads(token, max_age=max_age)
            if not user_channels or not self.channel or self.channel in user_channels:
                self.user_id = user_id
                self.user_channels = user_channels
        except BadSignature as e:
            pass

    def on_unauthorized(self):
        self.send_error(403)

    def on_authorized(self):
        self.auth_done = True


class RedisMixin(object):
    def create_client(self):
        self.client = self.application.create_brukva_client()
        self.subscribed = False

    def subscribe(self, *channels):
        def on_subscribe(*args):
            self.client.listen(self.on_redis_message)
            self.subscribed = True
            self.subscribed_to = channels
        self.client.subscribe(channels, on_subscribe)

    def unsubscribe(self, callback=None):
        if not self.client or not self.subscribed:
            if callback:
                callback()
            return
        def cb():
            self.subscribed = False
            if callback:
                callback()
        self.client.unsubscribe(self.subscribed_to, callback=cb)

    def close_client(self, callback=None):
        def on_unsubscribe(*args):
            # if self.client:
            #     self.client.disconnect()
            logger.debug('Client disconnected')
            if callback:
                callback()
        if self.subscribed:
            self.unsubscribe(on_unsubscribe)
        else:
            on_unsubscribe()


class WebSocketMixin(object):
    heartbeat_interval = 60
    heartbeat_timeout = 30

    def send_error(self, code, **kwargs):
        self.close()

    def check_origin(self, origin):
        return True

    def start_heartbeat(self, interval=None, timeout=None):
        self.heartbeat = True
        if interval is not None:
            self.heartbeat_interval = interval
        if timeout is not None:
            self.heartbeat_timeout = timeout

        def close_on_timeout():
            logger.debug('Ping timeout')
            self.heartbeat_timeout_cb = None
            self.heartbeat = False
            self.close()
            self.on_close()

        self.heartbeat_timeout_cb = ioloop.IOLoop.instance()\
            .call_later(self.heartbeat_timeout, close_on_timeout)
        logger.debug('Pinging...')
        self.ping('ping')

    def on_pong(self, data):
        logger.debug('Pong')
        if self.heartbeat_timeout_cb:
            ioloop.IOLoop.instance().remove_timeout(self.heartbeat_timeout_cb)
            self.heartbeat_timeout_cb = None
        if getattr(self, 'heartbeat', False):
            ioloop.IOLoop.instance().call_later(
                self.heartbeat_interval, self.start_heartbeat)
