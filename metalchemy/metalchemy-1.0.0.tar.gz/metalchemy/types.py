"""Custom sqlalchemy types."""
import json

from sqlalchemy.types import TypeDecorator, TEXT


class JSONEncodedText(TypeDecorator):

    """Represents an immutable structure as a json-encoded string.

    Usage::

        JSONEncodedDict(255)
    """

    impl = TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value
