
from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru
import StringIO
import tempfile
import os
import urllib
import logging

from jss.connection import JssClient


class Storage(driver.Base):

    def __init__(self, path=None, config=None):
        self._access_key = config.jss_accesskey
        self._secret_key = config.jss_secretkey
        self._bucket = config.jss_bucket
        self._domain = config.jss_domain
        print "==========================>access_key:"+config.jss_accesskey
        print "==========================>jss_secretkey:"+config.jss_secretkey
        print "==========================>jss_bucket:"+config.jss_bucket
        print "==========================>jss_domain:"+config.jss_domain
        
        self._jss = JssClient(self._access_key, self._secret_key, self._domain, '80')
        
    def _init_path(self, path=None):
        if path:
            return path.split("/")[2]
        return path

    def content_redirect_url(self, path):
        print "content_redirect_url path:"+path
        path = self._init_path(path)
        object_instance = self._jss.bucket(self._bucket).object(path)
        
        return object_instance.generate_url("GET")

    @lru.get
    def get_content(self, path):
        print "get_content path:"+path
        path = self._init_path(path)
        output = StringIO.StringIO()
        try:
            object_instance = self._jss.bucket(self._bucket).object(path)
            res = object_instance.download_flow()
            while True:
                data = res.read(1024)
                if len(data) != 0:
                    output.write(data)
                else:
                    break
                    
            return output.getvalue()
        except Exception as e:
            print e
            raise e

    
    @lru.set
    def put_content(self, path, content):
        print "put_content path:"+path
        path = self._init_path(path)
        try:
            object_instance = self._jss.bucket(self._bucket).object(path)
            object_instance.upload_flow(None, None, content)
        except Exception as e:
            print e
            raise e
        return path

    def stream_write(self, path, fp):
        print "stream_write path:"+path
        path = self._init_path(path)
        part_size = 5 * 1024 * 1024
        if self.buffer_size < part_size:
            part_size = self.buffer_size
        try:
             object_instance = self._jss.bucket(self._bucket).object(path)
             object_instance.multi_upload_fp(None, None, fp, part_size)
        except Exception as e :
            print e
            raise e

    @lru.remove
    def remove(self, path):
        print "remove path:"+path
        path = self._init_path(path)

        try:
           self._jss.bucket(self._bucket).delete_key(path)
        except Exception as e:
            print e
            raise e
