from json_resource import (
    ResourceNotFound, ResourceExists, ValidationError
)

from flask.ext.json_resource.authorization import (
    Forbidden, UnAuthorized, ServiceUnavailable
)

class InvalidResource(Exception):
    pass


