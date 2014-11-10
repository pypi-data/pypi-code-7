import json
import requests

from json_resource_http.exceptions import (
    ResourceNotFound, ResourceExists, Forbidden, UnAuthorized, InvalidResource,
    ValidationError, ServiceUnavailable
)


class HTTPQuerySet(object):
    def __init__(self, resource, **kwargs):
        self.resource = resource
        self._result = None

    def __len__(self):
        return len(self._result)

    def _reset(self):
        self._result = None

    def _raise(self, response):
        if response.status_code == 404:
            raise ResourceNotFound(response.request.url)
        elif response.status_code == 409:
            raise ResourceExists(response.request.url)
        elif response.status_code == 401:
            raise UnAuthorized(response.request.url)
        elif response.status_code == 403:
            raise Forbidden(response.request.url)
        elif response.status_code == 422:
            raise ValidationError(
                json.loads(response.content)
            )
        else:
            raise InvalidResource(response.content)

    def next(self):
        if not self._result:
            self._result = requests.get(self.resource().rel('collection'))

        return self._resource(self._result.next())

    def load(self, resource, url=None):
        url = url or resource.url

        try:
            response = requests.get(url, headers=resource.headers)
        except requests.ConnectionError:
            raise ServiceUnavailable(url)

        if response.status_code != 200:
            raise self._raise(response)

        try:
            data = json.loads(response.content)
        except ValueError:
            raise InvalidResource(response.content)

        resource.update(data)

    def insert(self, resource, validate=True):
        response = requests.post(
            resource.rel('create'),
            data=json.dumps(resource),
            headers=resource.headers
        )

        if response.status_code != 201:
            self._raise(response)

        try:
            resource.clear()
            resource.update(json.loads(response.content))
        except ValueError, e:
            raise InvalidResource(e)

    def save(self, resource, validate=True, upsert=True):
        response = requests.put(
            resource.url,
            data=json.dumps(resource),
            headers=resource.headers
        )

        if response.status_code != 200:
            self._raise(response)

    def patch(self, resource, patch):
        response = requests.patch(
            resource.url,
            headers=resource.headers,
            data=json.dumps(patch)
        )

        if response.status_code != 200:
            self._raise(response)

        try:
            resource.clear()
            resource.update(json.loads(response.content))
        except ValueError, e:
            raise InvalidResource(e)

    def delete(self, resource):
        response = requests.delete(
            resource.url,
            headers=resource.headers
        )

        if response.status_code != 204:
            self._raise(response)
