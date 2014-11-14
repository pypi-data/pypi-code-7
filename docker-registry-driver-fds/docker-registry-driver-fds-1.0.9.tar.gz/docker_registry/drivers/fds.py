
from docker_registry.core import driver
from docker_registry.core import exceptions
from docker_registry.core import lru

#import fds
import fds.GalaxyFDSClient
class Storage(driver.Base):

    supports_bytes_range = False

    def __init__(self, path=None, config=None):
      self._root_path = path or ''
      self.domain = config.fds_domain
      self.bucket = config.fds_bucket
      self.accesskey = config.fds_accesskey
      self.secretkey = config.fds_secretkey
      self.client =  fds.GalaxyFDSClient.GalaxyFDSClient(self.accesskey, self.secretkey)
      #self.client = fds.GalaxyFDSClient(self.accesskey, self.secretkey)

    # Remove the first and last "/" of path for FDS
    def _init_path(self, path=None):
        path = self._root_path + path if path else self._root_path
        if path:
            if path.startswith('/'):
                path = path[1:]
            if path.endswith('/'):
                path = path[:-1]
        return path

    # Get the object from FDS
    @lru.get
    def get_content(self, path):
        try:
            path = self._init_path(path)
            return self.client.get_object(self.bucket, path)
        except:
            raise exceptions.FileNotFoundError("File not found %s" % path)

    # Stream get object in FDS
    def stream_read(self, path, bytes_range=None):
        #self.buffer_size = 128 * 1024
        path = self._init_path(path)
        try:
            for i in self.client.stream_get_object(self.bucket, path, self.buffer_size):
                yield i
        except:
            raise exceptions.FileNotFoundError("File not found %s" % path)

    # Put the object in FDS
    @lru.set
    def put_content(self, path, content):
        try:
            path = self._init_path(path)
            self.client.put_object(self.bucket, path, content)
        except:
          raise IOError("Could not put content: %s" % path)
        return path

    # Get content from one by one and return the iterator for FDS sttreamPutObject()
    def yield_content(self, fp):
        #self.buffer_size = 128 * 1024
        while True:
            buf = fp.read(self.buffer_size)
            if not buf:
                break
            yield buf

    # Stream put object in FDS
    def stream_write(self, path, fp):
        path = self._init_path(path)
        self.client.stream_put_object(self.bucket, path, self.yield_content(fp))

    # Check if the object exists in FDS
    def exists(self, path):
        path = self._init_path(path)
        try:
            return self.client.does_object_exists(self.bucket, path)
        except Exception:
            raise IOError("Could not check object existence: %s" % path)
            return False

    # Delete the object in FDS
    @lru.remove
    def remove(self, path):
        path = self._init_path(path)
        try:
            self.client.delete_object(self.bucket, path)
            return
        except Exception:
            raise exceptions.FileNotFoundError("File not found %s" % path)

    # Get the object size in FDS
    def get_size(self, path):
        path = self._init_path(path)
        try:
            return self.client.get_object_size(self.bucket, path)
        except Exception:
            raise exceptions.FileNotFoundError("File not found %s" % path)

    # List the directories in FDS
    def list_directory(self, path=None):
        prefix = ''
        path = self._init_path(path)
        if path:
            path = '%s/' % path
        exists = False
        try:
            for d in self.client.list_directories_and_objects(self.bucket, path):
                exists = True
                yield d
        except Exception:
            pass
        if not exists:
            raise exceptions.FileNotFoundError("File not found %s" % path)
