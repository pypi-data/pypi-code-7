from copy import deepcopy
import uuid

from ontic import ontic_type
from ontic.validation_exception import ValidationException

from phenomena.config_lock import config_lock
from phenomena.connection_types import Listener, Requester, Responder, Sink


class ConnectionManager(object):
    def __init__(self, event_core):
        """

        :param event_core:
        :type event_core: phenomena.event_core.EventCore
        """
        self.event_core = event_core
        self.log = event_core.log

        self._listener_configs = {}
        self._requester_configs = {}
        self._responder_configs = {}
        self._sink_configs = {}

    @property
    def listener_configs(self):
        return deepcopy(self._listener_configs)

    @property
    def requester_configs(self):
        return deepcopy(self._requester_configs)

    @property
    def responder_configs(self):
        return deepcopy(self._responder_configs)

    @property
    def sink_configs(self):
        return deepcopy(self._sink_configs)

    @config_lock
    def register_listener(self,
                          address='localhost',
                          port=60053,
                          protocol='tcp',
                          type='pull'):
        listener = Listener(
            id=int(uuid.uuid4()),
            address=address,
            port=port,
            protocol=protocol,
            type=type)
        self.log.info('register_listener: %s', listener)

        try:
            ontic_type.validate_object(listener)
        except ValidationException as ve:
            raise ValueError(ve.message)

        self._listener_configs[listener.id] = listener

        # todo: raulg - add activating the listener if the core is running

        return deepcopy(listener)

    @config_lock
    def register_requester(self,
                           address='localhost',
                           port=60053,
                           protocol='tcp',
                           type='request'):
        requester = Requester(
            id=int(uuid.uuid4()),
            address=address,
            port=port,
            protocol=protocol,
            type=type)
        self.log.info('register_requester: %s', requester)

        try:
            ontic_type.validate_object(requester)
        except ValidationException as ve:
            raise ValueError(ve.message)

        self._requester_configs[requester.id] = requester

        # todo: raulg - add activating the requester if the core is running

        return deepcopy(requester)

    @config_lock
    def register_responder(self,
                           address='*',
                           port=60053,
                           protocol='tcp',
                           type='reply'):

        responder = Responder(
            id=int(uuid.uuid4()),
            address=address,
            port=port,
            protocol=protocol,
            type=type)
        self.log.info('register_responder: %s', responder)

        try:
            ontic_type.validate_object(responder)
        except ValidationException as ve:
            raise ValueError(ve.message)

        self._responder_configs[responder.id] = responder

        # todo: raul - add the actual code
        return deepcopy(responder)


    @config_lock
    def register_sink(self,
                      address='*',
                      port=60053,
                      protocol='tcp',
                      type='push'):
        sink = Sink(
            id=int(uuid.uuid4()),
            address=address,
            port=port,
            protocol=protocol,
            type=type)
        self.log.debug('register_sink: %s', sink)

        try:
            ontic_type.validate_object(sink)
        except ValidationException as ve:
            raise ValueError(ve.message)

        self.sink_configs[sink.id] = sink

        # todo: raulg - add activating the sink if the core is running

        return deepcopy(sink)
