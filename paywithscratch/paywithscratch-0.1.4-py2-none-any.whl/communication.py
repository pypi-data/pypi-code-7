from json import dumps as json_encode
from openid.consumer.consumer import FAILURE, SUCCESS, Consumer
from openid.oidutil import autoSubmitHTML
from urlparse import urlparse, urlunparse

from .extension import Auth_OpenID_Scratch

class ScratchException(Exception):
    def __init__(self, message):
        self.message = message

class ScratchPage(object):
    default_site = "http://paywithscratch.com/"
    
    def __init__(self, session, store, scratch_site=None):
        self.session = session
        self.store = store
        self.server = scratch_site or self.default_site
    
    def begin(self, redirect, transaction, refid, api_key, secret):
        consumer = Consumer(self.session, self.store)
        auth_request = consumer.begin(self.server)
        auth_request.addExtension(Auth_OpenID_Scratch(transaction, refid, api_key, secret))
        fields = urlparse(redirect)
        realm = urlunparse((fields.scheme, fields.netloc, '/', '', '', ''))
        message = auth_request.getMessage(realm, redirect)
        return ScratchVars(auth_request.endpoint.server_url, message)
    
    def complete(self, params, location):
        # On Success, return the validated Scratch parameters.
        # On Failure, return None.
        # On Error, raise an exception.
        
        consumer = Consumer(self.session, self.store)
        response = consumer.complete(params, location)
        result = None
        
        if response.status == SUCCESS:
            result = response.message.getArgs(Auth_OpenID_Scratch.ns_uri)
        elif response.status == FAILURE:
            raise ScratchException(response.message)
        
        return result

class ScratchVars(object):
    def __init__(self, server, message):
        self.server = server
        self._msg = message
    
    def params(self):
        return self._msg.toPostArgs()
    
    def form(self):
        # This is the main reason to keep the Message around.
        # No need to duplicate logic just yet...
        return self._msg.toFormMarkup(self.server)
    
    def html(self):
        return autoSubmitHTML(self.form())
    
    def json(self):
        return json_encode(self.params())
