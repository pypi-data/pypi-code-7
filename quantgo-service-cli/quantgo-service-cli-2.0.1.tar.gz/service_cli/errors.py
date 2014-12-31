class BaseQuantGoError(Exception): pass

# Client
class ClientError(BaseQuantGoError): pass

# Server
class ServerError(BaseQuantGoError): pass
