
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
        print "==========================>"+config.jss_accesskey
        self._jss = JssClient(self._access_key, self._secret_key, self._domain, "80")
        
    def _init_path(self, path=None):
        if path:
            path.split("/")[2]
        return path

    def content_redirect_url(self, path):
        path = self._init_path(path)
        object_instance = self._jss.bucket(self._bucket).object(path)
        
        return object_instance.generate_url("GET")

    def get_json(self, path):
        try:
            return json.loads(self.get_unicode(path))
        except:
            return []

    @lru.get
    def get_content(self, path):
        path = self._init_path(path)

        output = StringIO.StringIO()
        try:
            return self._jss.bucket(self._bucket).get_Key(path)
        except Exception as e:
            raise e

    
    @lru.set
    def put_content(self, path, content):
        print self
        print path
        path = self._init_path(path)
        try:
            object_instance = self._jss.bucket(self._bucket).object(path)
            object_instance.upload_flow(None, content)
        except Exception as e:
            print e
            raise e
        return path

    def stream_write(self, path, fp):
        path = self._init_path(path)
        part_size = 5 * 1024 * 1024
        if self.buffer_size < part_size:
            part_size = self.buffer_size
        try:
             object_instance = self._jss.bucket(self._bucket).object(path)
             object_instance.multi_upload_fp(None, None, fp, part_size)
        except Exception as e :
            raise e

    @lru.remove
    def remove(self, path):
        path = self._init_path(path)

        try:
           self._jss.bucket(self._bucket).delete_key(path)
        except Exception as e:
            raise e
