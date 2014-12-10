from enum import Enum


class LivefyreException(Exception):
    pass
    

class ApiException(LivefyreException):
    def __init__(self, code):
        status = ApiStatus.by_code(code)
        super(ApiException, self).__init__(status.msg)


class ApiStatus(Enum):
    BAD_REQUEST = (400, 'Please check the contents of your request. Error code 400.')
    UNAUTHORIZED = (401, 'The request requires authentication via an HTTP Authorization header. Error code 401.')
    NOT_AUTHORIZED = (403, 'The server understood the request, but is refusing to fulfill it. Error code 403.')
    RESOURCE_NOT_FOUND = (404, 'The requested resource was not found. Error code 404.')
    SERVER_ERROR = (500, 'Livefyre appears to be down. Please see status.livefyre.com or contact us for more information. Error code 500.')
    NOT_IMPLEMENTED = (501, 'The requested functionality is not currently supported. Error code 501.')
    BAD_GATEWAY = (502, 'The server, while acting as a gateway or proxy, received an invalid response from the upstream server it accessed in attempting to fulfill the request at this time. Error code 502.')
    SERVER_UNAVAILABLE = (503, 'The service is undergoing scheduled maintenance, and will be available again shortly. Error code 503.')
    
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    
    @staticmethod
    def by_code(code):
        for status in ApiStatus.__members__.values():
            if int(code) == status.code:
                return status
        raise ValueError('Error code {} has not been accounted for! Please contact us at tools@livefyre.com with this message.'.format(code))
