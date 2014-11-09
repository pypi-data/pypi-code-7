class FaneryException(Exception):
    pass


class MultipleDefine(FaneryException):
    pass


class UndefinedOutputFormatter(FaneryException):
    pass


class InvalidOutputFormatter(FaneryException):
    pass


class CallPadsLimitExceeded(FaneryException):
    pass


class InvalidCall(FaneryException):
    pass


class NotFound(FaneryException):
    pass


class Abusive(FaneryException):
    pass


class Forbidden(FaneryException):
    pass


class Unauthorized(FaneryException):
    pass


class RequireSSL(FaneryException):
    pass


class CallPadTimeout(FaneryException):
    pass


class ExpiredSession(FaneryException):
    pass


class UnknownSession(FaneryException):
    pass


class InvalidCredential(FaneryException):
    pass


class MaxActiveSessions(FaneryException):
    pass


class UnknownModel(FaneryException):
    pass


class DuplicatedRecordID(FaneryException):
    pass


class RecordValidationError(FaneryException):
    pass


class RecordVersionMismatch(FaneryException):
    pass


class RecordNotFound(FaneryException):
    pass


class UnstoredRecord(FaneryException):
    pass


class DeletedRecord(FaneryException):
    pass


class MultipleRecordsFound(FaneryException):
    pass


class RecordMarkedForDeletion(FaneryException):
    pass


class RecordMarkedForInsertion(FaneryException):
    pass
