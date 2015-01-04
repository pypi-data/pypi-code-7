# coding: utf-8


class InternalError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return '{0}: {1}'.format(self.code, self.message)


class Invalid(InternalError):
    pass


class InvalidDictionary(Invalid):
    pass


class InvalidEntryId(Invalid):
    pass


class PageNotFound(Invalid):
    pass


class NoResults(Invalid):
    pass