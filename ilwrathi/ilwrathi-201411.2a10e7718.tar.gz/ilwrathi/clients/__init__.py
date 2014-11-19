#!/usr/bin/env python
import requests

###############################################################################
# Exceptions
###############################################################################
class ClientError(Exception):

    pass


###############################################################################
# Clients
###############################################################################

class RestJSON:
    history = []

    def __init__(self, baseurl, proxies=None):
        self.baseurl = baseurl
        self.session = requests.session()
        self.session.proxies = proxies
        self.session.hooks["response"].append(self.__add_history)

        def __getattr__(self, name):
        if name in self.__class__.__dict__:
            return self.__class__.__dict__[name]
        method, endpoint = name.split('_',1)
        endpoint = '/'.join(endpoint.split('_'))
        target = self.baseurl + '/' +  endpoint
        return self.__class__.__dict__['_' + method](self, target)

    def _get(self, target):
        def _func(*args,**kwargs):
            args = '/'.join(str(a) for a in args)
            url = target + '/' + args 
            if kwargs:
                url += '?' + '&'.join("%s=%s" % i for i in kwargs.items())
            return self.session.get(url)
        return _func

    def _post(self, target):
        url = target
        def _func(jdict):
            return self.session.post(target, data=json.dumps(jdict), 
                                 headers=headers)
        return _func
    
    def _put(self, target):
        url = target
        def _func(jdict):
            return self.session.put(target, data=json.dumps(jdict), 
                                headers=headers)
        return _func
    
    def _delete(self, target):
        def _func(*args,**kwargs):
            args = '/'.join(str(a) for a in args)
            url = target + '/' + args 
            return self.session.delete(url)
        return _func

    def __add_history(self, response, *args, **kwargs):
        self.history.append(response)

    
