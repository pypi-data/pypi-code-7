import json


class ValidationError(Exception):
    def __init__(self, errors):
        if not isinstance(errors, dict):
            self.errors = dict(
                [('/' + '/'.join(error.path), error.message) for error
                 in errors]
            )
        else:
            self.errors = errors

        super(ValidationError, self).__init__(json.dumps(self.errors))


class ResourceNotFound(Exception):
    pass


class ResourceExists(Exception):
    pass



