from json_resource import ResourceNotFound, ResourceExists, ValidationError

class Forbidden(Exception):
    pass


class UnAuthorized(Exception):
    pass


class InvalidResource(Exception):
    pass


