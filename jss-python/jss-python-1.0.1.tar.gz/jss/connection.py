# -*- coding: utf-8 -*-  
'''
Created on 2013-7-23

@author: root
'''
from conf import mime_type
from jss import commonconstants
from jss.bucket import Bucket
from jss.util import error_handler, bucket_name_check
from urllib import quote
import base64
import hashlib
import hmac
import httplib
import json
import logging
import os.path
import sys
import time


_Default = object()

# logging.config.fileConfig(CONF_LOG); 
# logger = logging.getLogger("root")  


class JssClient(object):
    '''
    classdocs
    '''
    
    def __init__(self, access_key=None, secret_key=None, host=None, port=None, strict=False, timeout=None, maxsize=None,
                 block=False, headers=None, is_security=False):
        self.access_key = access_key
        self.secret_key = secret_key
        self.map = mime_type.mime_map
        self.host = host
        self.port = port
        self.pool = None
        self.is_security = is_security
        if not timeout:
            self.timeout = timeout
        else:
            self.timeout = 10
            
            
    def __iter__(self):
        bucketresults = self.get_all_buckets() 
        for curr_bucket in bucketresults['bucketlist']:
            yield self.bucket(curr_bucket['Name']) 
             
    def __contain__(self, bucket_name):
        self.has_bucket(bucket_name)  
            
                        
    def get_connection(self):    
        if self.is_security or self.port == 443:
            self.is_security = True
            if sys.version_info >= (2, 6):
                self.pool = httplib.HTTPSConnection(host=self.host, port=self.port, timeout=self.timeout)
            else:
                self.pool = httplib.HTTPSConnection(host=self.host, port=self.port)
        else:
            if sys.version_info >= (2, 6):
                self.pool = httplib.HTTPConnection(host=self.host, port=self.port, timeout=self.timeout)
            else:
                self.pool = httplib.HTTPConnection(host=self.host, port=self.port)    
            
    def get_credentials(self, method, url_resource, headers=None):
        if  headers:
            if 'Content-MD5' in headers:
                content_md5 = headers.get('Content-MD5')
            else:
                content_md5 = ''
            if 'Content-Type' in headers:
                content_type = headers.get('Content-Type')
            else:
                content_type = ''
        else:
            content_md5 = ''
            content_type = ''
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())    
        string_to_sign = method + \
                         "\n" + content_md5 + \
                         "\n" + content_type + \
                         "\n" + date + \
                         "\n" + url_resource
                         
        # print string_to_sign
        signature = base64.encodestring(hmac.new(str(self.secret_key), \
            string_to_sign, hashlib.sha1).digest()).strip()
        authorization = "jingdong" + " " + self.access_key + ":" + signature
        return authorization  
    
    def open_connection_to_put(self, method, bucket_name, object_name=None, headers=None, query_args=None, subresource=None):

        if not headers:
            headers = {}
        method = 'PUT'
        path = self._build_path_base(bucket_name, object_name, query_args)
        path_au = self._build_path_base_AU(bucket_name, object_name, subresource)
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        self.get_connection()
        #print self.host
        #print self.port
        #print path
        self.pool.putrequest(method, path)
        if not headers:
            headers = {}
        headers['User-Agent'] = 'JSS-SDK-PYTHON/1.0.1'
        headers['Date'] = date
        headers['Authorization'] = self.get_credentials(method, path_au, headers)
        headers["Expect"] = "100-Continue"
        for k in headers.keys():
            self.pool.putheader(k, str(headers[k]))
            #print "%s\t%s" % (str(k), str(headers[k]))
        self.pool.endheaders()
        return self.pool
    
    def  send(self,data):
        self.pool.send(data)    
             
    def make_request(self, method, bucket_name=None, object_name=None, headers=None, data='', query_args=None, subresource=None):
        
        path = self._build_path_base(bucket_name, object_name, query_args)
        path_au = self._build_path_base_AU(bucket_name, object_name, subresource)
        date = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime())
        if not headers:
            headers = {}
        headers['User-Agent'] = 'JSS-SDK-PYTHON/1.0.1'
        headers['Date'] = date
        headers['Authorization'] = self.get_credentials(method, path_au, headers)
        self.get_connection()
        retry = 6
        while retry > 0:
            retry = retry - 1
            self.pool.request(method, path, data, headers)
            res = self.pool.getresponse()
            if res.status == 301 or res.status == 302:
                continue
            else:
                return res

    def _build_path_base_AU(self, bucket_name, object_name, query_args=None):
        path_base = '/'
        if bucket_name:
            path_base += "%s" % quote(bucket_name)
        if object_name:
            path_base += "/%s" % object_name
        if query_args:
            path_base += '?' + query_args   
        return path_base           

    def _build_path_base(self, bucket_name, object_name, query_args=None):
        path_base = '/'
        if bucket_name:
            path_base += "%s" %quote(bucket_name)
        if object_name:
            path_base += "/%s" %quote(object_name)
        if query_args:
            path_base += '?' + query_args   
        return path_base
    
    def create_bucket(self, bucket_name, headers=None):
        """
        creates a new bucket 
        
        type bucket_name: string
        :param bucket_name :The name of a new bucket
        
        type headers: dict
        :param headers: Additional headers to pass along with the request to JSS
        
        """
        bucket_name_check(bucket_name)
        if not headers:
        	headers={}
    	headers['Content-Length']=0
        response = self.make_request('PUT', bucket_name=bucket_name, headers=headers)
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return response
        
    def delete_bucket(self, bucket_name, headers=None):
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
        response = self.make_request(method='DELETE', bucket_name=bucket_name, headers=headers)
        if response.status / 100 > 2:
            error_handler(response)
        else:
            return response

    def get_all_buckets(self, headers=None):
        headers = {}
        headers['Content-Type'] = 'application/json'
        response = self.make_request(method='GET', headers=headers)  
        if response.status / 100 > 2:
            error_handler(response)
        else:
            data = response.read()
            bucketlist = json.loads(data, 'UTF-8')
            result = {}
            result['size'] = bucketlist['Buckets'].__len__()
            result['bucketlist'] = bucketlist['Buckets']
            result['max-size'] = commonconstants.MAX_BUCKETS_SIZE
            return result
                
    def print_all_buckets(self, headers=None):
        result = self.get_all_buckets(headers)
        print json.dumps(result, 'UTF-8', indent=4, ensure_ascii=False, sort_keys=True)
        
    def bucket(self, bucket_name):
    
        return Bucket(self, bucket_name)  
     
    def has_bucket(self, bucket_name):
        result = self.get_all_buckets()
        if result['bucketlist']:
            for bucket_mumb in result['bucketlist']:
                if bucket_mumb['Name'] == bucket_name:
                    return True
        return False
                          
