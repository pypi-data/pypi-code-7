# -*- coding: utf-8 -*-  
'''
Created on 2013-7-23

@author: root
'''
from jss import key
from jss.exception import StorageError
from jss.util import error_handler
import json
import urllib

class Bucket(object):
    '''
    classdocs
    '''
    def  __init__(self, jss_client=None, name=None, key_class=key.Key):
        self.name = name
        self.jss_client = jss_client
        self.key_class = key_class
        
    def __repr__(self):
        return '<Bucket: %s>' % self.name
    
    def __iter__(self):
        keylist = self.get_all_keys()
        for curr in keylist['Contents']:
            yield  self.key_class(self, curr['Key'])

    def __contains__(self, key_name):
        return not (self.get_key(key_name) is None)
    
    def create(self, headers=None):
        """
        create a new bucket 
        
         type headers: dict
        :param headers: Additional headers to pass along with the request to JSS
        
        """
        return self.jss_client.create_bucket(self.name, headers)
    
    
    def delete(self, headers=None):
        """
        Removes an JSS bucket.

        In order to remove the bucket, it must first be empty. If the bucket is
        not empty, an ``StorageError`` will be raised.

        :type bucket_name: string
        :param bucket_name: The name of the bucket

        :type headers: dict
        :param headers: Additional headers to pass along with the request to
            JSS.
        """
        return self.jss_client.delete_bucket(self.name, headers)
    
    def get_key(self, object_name):
        headers = {}
        response = self.jss_client.make_request(method='GET', bucket_name=self.name, object_name=object_name, headers=headers)
        if response.status / 100 > 2:
            if response.status == 404:
                return None
            else:
                raise StorageError(response.status, response.reason,
                       '', '', '', '')
        else:
            #print response.getheaders().__str__()
            k = self.key_class(self, object_name)
            for key, value in response.getheaders():
                if key == 'etag':
                    k.etag = value
                if key == 'content-type':
                    k.content_type = value,
                if key == 'content-disposition':
                    k.content_disposition = value
                if key == 'content-length':
                    k.content_length = value
                    #print value
            return k 
        
    def get_all_keys(self, headers=None, prefix='', delimiter='', marker='', maxKeys=''):
        headers = {}
        headers['Content-Type'] = 'application/json'
        params = {}
        if prefix:
            params['prefix'] = prefix
        if delimiter:
            params['delimiter'] = delimiter
        if  marker:
            params['marker'] = marker
        if maxKeys:
            params['maxKeys'] = maxKeys
        l = []
        for k, v in params.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (k, v))
        if len(l):
             query_string = '&'.join(l)
             #print query_string
        else:
             query_string = None        
        response = self.jss_client.make_request(method='GET', bucket_name=self.name, object_name=None, headers=headers, data='', query_args=query_string)
        data = response.read()
        keylist = json.loads(data)
       
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return keylist
        
    def new_key(self, key_name=None):
        """
        Creates a new key

        :type key_name: string
        :param key_name: The name of the key to create

        :rtype: :class:`boto.s3.key.Key` or subclass
        :returns: An instance of the newly created key object
        """
        if not key_name:
            raise ValueError('Empty key names are not allowed')
        return self.key_class(self, key_name)
    
    def delete_key(self, key_name):
        
        response = self.jss_client.make_request(method='DELETE', bucket_name=self.name, object_name=key_name)
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return response
    
    def object(self, object_name):
        return key.Key(self, object_name)
    
    def print_all_keys(self, headers=None):
        result = self.get_all_keys(headers)
        print json.dumps(result, 'UTF-8', indent=4, ensure_ascii=False, sort_keys=True)
        
    def list_multi_uploads(self,headers=None,key_marker=None,upload_id_marker=None,max_uploads=None,prefix=None,delimiter=None):
        param={}
        l=[]
        query_param=''
        if key_marker:
            param['key-marker']=key_marker
        if upload_id_marker:
            param['upload-id-marker']=upload_id_marker
        if max_uploads:
            param['max-uploads']=max_uploads
        if prefix:
            param['prefix']=prefix
        if delimiter:
            param['delimiter']=delimiter
        for k, v in param.items():
            if isinstance(v, unicode):
                v = v.encode('utf-8')
            if v is not None and v != '':
                l.append('%s=%s' % (urllib.quote(k), urllib.quote(str(v))))
        if len(l):
            query_param = '&'.join(l) 
        if query_param:
            subresource = 'uploads&'+query_param
        else:
            subresource='uploads'    
        response = self.jss_client.make_request(method='GET', bucket_name=self.name, headers=headers, data='', query_args=subresource, subresource=subresource) 
        if response.status/100!=2:
            error_handler(response)
        return  response
    
