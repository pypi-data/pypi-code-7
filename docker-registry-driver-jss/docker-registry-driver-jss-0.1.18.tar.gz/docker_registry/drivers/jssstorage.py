
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
        path1 = self._init_path(path)
        object_instance = self._jss.bucket(self._bucket).object(path1)
        
        return object_instance.generate_url("GET")
    
    @lru.get
    def get_content(self, path):
        logger.info("get_content path:%s" % path)
        path1 = self._init_path(path)
        output = StringIO.StringIO()
        try:
            object_instance = self._jss.bucket(self._bucket).object(path1)
            res = object_instance.download_flow()
            while True:
                data = res.read(1024)
                if len(data) != 0:
                    output.write(data)
                else:
                    break
                    
            return output.getvalue()
        except Exception as e:
            logger.error("get_content error:%s" % e)
            raise exceptions.FileNotFoundError("File not found %s" % path)
        finally:
            output.close()

    
    @lru.set
    def put_content(self, path, content):
        logger.info("put_content path:%s" % path)
        path1 = self._init_path(path)
        try:
            object_instance = self._jss.bucket(self._bucket).object(path1)
            object_instance.upload_flow(None, None, content)
        except Exception as e:
            logger.error("put_content error:%s" % e)
            raise e
        return path

    def stream_write(self, path, fp):
        logger.info("stream_write path:%s" % path)
        path1 = self._init_path(path)
        part_size = 5 * 1024 * 1024
        if self.buffer_size < part_size:
            part_size = self.buffer_size
        try:
             object_instance = self._jss.bucket(self._bucket).object(path1)
             object_instance.multi_upload_fp(None, None, fp, part_size)
        except Exception as e :
            logger.error("stream_write error:%s" % e)
            raise e

    @lru.remove
    def remove(self, path):
        logger.info("remove path:%s" % path)
        path1 = self._init_path(path)

        try:
           self._jss.bucket(self._bucket).delete_key(path1)
        except Exception as e:
            logger.error("remove error:%s" % e)
            raise e
