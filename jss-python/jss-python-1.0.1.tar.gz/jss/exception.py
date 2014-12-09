# -*- coding: utf-8 -*-  
'''
Created on 2013-7-23

@author: root
'''

class StorageError(StandardError):
    def __init__(self, status, reason, error_code=None, error_msg=None, resource=None , request_id=None, *args):
        self.status = status
        self.reason = reason
        self.error_code = error_code
        self.error_msg = error_msg
        self.resource = resource
        self.request_id = request_id
        
    def __str__(self):
        return 'StorageError:  errorMessage: %s,resource:%s,requestId:%s' % (self.error_msg, self.resource, self.request_id)

    