import json_resource

from json_resource_http.queryset import HTTPQuerySet


class HTTPResourceMeta(json_resource.StoredResourceMeta):
    """ Metaclass that add an `objects` member to the class.

    The objects member is a queryset that allows creating, querying and deleting
    resources of the class.
    """
    def __new__(cls, name, bases, dct):
        result = json_resource.ResourceMeta.__new__(cls, name, bases, dct)

        if result.schema and not hasattr(result, 'objects'):
            result.objects = HTTPQuerySet(
                result
            )

        return result


class Resource(json_resource.Resource):
    __metaclass__ = HTTPResourceMeta

    def __init__(self, data, headers=None, **kwargs):
        self._headers = headers or {}

        super(Resource, self).__init__(data, **kwargs)

    def patch(self, patch):
        return self.objects.patch(self, patch)

    def save(self, create=False, validate=True, **kwargs):
        if create:
            if validate:
                self.validate(create=True)

            validate = False

        super(Resource, self).save(create=create, validate=validate, **kwargs)

    @property
    def headers(self):
        headers = {
            'content-type': 'application/json'
        }

        headers.update(self._headers)

        return headers
