import datetime


class EventInspector(object):
    """Introspection object that has access to the internals of a
    :class:`ddd.event.Event` subclass.
    """

    def to_dto(self, event):
        """Convert the :class:`~ddd.event.Event` to a Data Transfer
        Object (DTO).
        """
        meta = event.__meta__
        event_params = event.__properties__
        fields = {x.name: event_params[x.name] for x in meta.get_fields()}
        fields['timestamp'] = event.__timestamp__
        return meta.dto_type(**fields)
