
from ontic.ontic_type import OnticType
from ontic.schema_type import SchemaType


class Listener(OnticType):
    ONTIC_SCHEMA = SchemaType({
        'id': {
            'type': long,
            'required': True,
        },
        'type': {
            'type': basestring,
            'required': True,
            'default': 'pull',
            'enum': {'pull'},
        },
        'protocol': {
            'type': basestring,
            'required': True,
            'default': 'tcp',
            'enum': {'tcp'},
        },
        'address': {
            'type': basestring,
            'required': True,
            'default': '*'
        },
        'port': {
            'type': int,
            'required': True,
            'default': 60053,
            'min': 0,
        }
    })
