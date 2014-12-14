from ontic.ontic_type import OnticType
from ontic.schema_type import SchemaType

from phenomena.connection_types import Listener


class CommandMessage(OnticType):
    CMD_RUN = 1
    CMD_MSG = 0
    CMD_KILL = -1

    _data_type_by_method = {
        'add_listener': Listener,
    }

    _methods = set(_data_type_by_method.keys())

    @classmethod
    def type_data_for_method(cls, method, data):
        data_type = cls._data_type_by_method.get(method)

        if data_type:
            return data_type(data)
        else:
            raise ValueError('Unknown method: %s', method)

    ONTIC_SCHEMA = SchemaType({
        'cmd': {
            'type': 'int',
            'required': True,
            'enum': {CMD_RUN, CMD_MSG, CMD_KILL}
        },
        'method': {
            'type': 'str',
            'enum': _methods,
        },
        'data': {
            'type': 'dict',
            'default': {},
        },
    })
