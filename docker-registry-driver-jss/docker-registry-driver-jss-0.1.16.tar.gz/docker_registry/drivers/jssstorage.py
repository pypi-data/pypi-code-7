
from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru
import StringIO
import tempfile
import os
import urllib
import logging

from jss.connection import JssClient

logger = logging.getLogger(__name__)

class Storage(driver.Base):

    def __init__(self, path=None, config=None):
        self._access_key = config.jss_accesskey
        self._secret_key = config.jss_secretkey
        self._bucket = config.jss_bucket
        self._domain = config.jss_domain
        logger.info("==========================>access_key:%s" % config.jss_accesskey)
        logger.info("==========================>jss_secretkey:%s" % config.jss_secretkey)
        logger.info("==========================>jss_bucket:%s" % config.jss_bucket)
        logger.info("==========================>jss_domain:%s" % config.jss_domain)
        
        self._jss = JssClient(None, self._access_key, self._secret_key, self._domain, None)
        
    def _init_path(self, path=None):
        if path:
            return path.split("/")[2]
        return path

    def content_redirect_url(self, path):
        logger.info("content_redirect_url path:%s" % path)
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
        logger.info("get_content path:%s" % path)
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
        finally:
            output.close()

    
    @lru.set
    def put_content(self, path, content):
        logger.info("put_content path:%s" % path)
        path = self._init_path(path)
        try:
            object_instance = self._jss.bucket(self._bucket).object(path)
            object_instance.upload_flow(None, None, content)
        except Exception as e:
            print e
            raise e
        return path

    def stream_write(self, path, fp):
        logger.info("stream_write path:%s" % path)
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
        logger.info("remove path:%s" % path)
        path = self._init_path(path)

        try:
           self._jss.bucket(self._bucket).delete_key(path)
        except Exception as e:
            print e
            raise e
