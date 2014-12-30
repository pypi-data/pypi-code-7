from ddd.event.metaclass import EventMetaclass


class Event(metaclass=EventMetaclass):

    @classmethod
    def deserialize(cls, raw_data, serializer):
        """Recreate an :class:`~ddd.event.Event` instance from a
        byte sequence containing the serialized parameters.

        Args:
            raw_data (bytes): the serialized event parameters.
            serializer (libtng.io.Serializer): a concrete serializer
                implementation.

        Returns:
            ddd.event.Event
        """
        return cls(**serializer.deserialize(raw_data))

    def __init__(self, *args, **kwargs):
        meta = self.__meta__

        # Iterate over all properties and add them to the private
        # state dictionary.
        for field in meta.get_fields():
            self.__properties__[field.name] = kwargs.pop(field.name, None)

    def serialize(self, serializer):
        """Serializes the :class:`~ddd.event.Event` using the
        provided `serializr`.
        """
        return serializer.serialize(self.__properties__)

    def __repr__(self):
        return "<Event: {0}>".format(self.__meta__.verbose_name)
