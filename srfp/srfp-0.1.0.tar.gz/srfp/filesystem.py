from fs.base import FS, NoDefaultMeta
from fs.filelike import FileLikeBase
from fs.errors import UnsupportedError, NoMetaError, ResourceNotFoundError, FSError, ResourceInvalidError
from fs.memoryfs import MemoryFile
from threading import Thread, Lock
from datetime import datetime
import sys
import os
import begin

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import logging
logger = logging.getLogger(__name__)

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

from .comms import MessageIO
from . import protocol

def proto2filename(name):
    name = [x for x in name if x]
    return os.path.join(*name)

def filename2proto(name):
    v = list(os.path.split(name))
    if v[0] == "/":
        del v[0]
    elif v[0].startswith("/"):
        v[0] = v[0][1:]
    return [x for x in v if x]

class SRFPFS (FS):
    def __init__(self, address):
        self.msgio = MessageIO(address)
        self.msg_q = Queue()
        thread = Thread(target=self._process_thread)
        thread.daemon = True
        thread.start()

    def get_meta(self, meta_name, default=NoDefaultMeta):
        if meta_name == "read_only":
            return True
        if default != NoDefaultMeta:
            return default
        raise NoMetaError()

    def _process_thread(self):
        while True:
            msg_to_send, resp_q = self.msg_q.get()
            self.msgio.send_msg(msg_to_send)
            resp_q.put(self.msgio.recv_msg())
            self.msg_q.task_done()

    def _msg_get(self, msg):
        resp_q = Queue()
        self.msg_q.put((msg, resp_q))
        response = resp_q.get()
        if isinstance(response, protocol.Error):
            pass # TODO: raise appropriate exception
            if response.code == protocol.Error.Codes.DOES_NOT_EXIST:
                logger.debug("ResourceNotFoundError")
                raise ResourceNotFoundError()
            else:
                logger.debug("FSError")
                raise FSError()
        else:
            return response

    def open(self, path, mode='r', buffering=-1, encoding=None, errors=None, newline=None, line_buffering=False, **kwargs):
        logger.debug("open: %s mode %s", path, mode)
        if 'w' in mode or 'a' in mode:
            raise UnsupportedError()

        # the isfile() call will also raise an exception if the file does not exist
        if not self.isfile(path):
            logger.debug("ResourceInvalidError: %s", path)
            raise ResourceInvalidError(path)

        return SRFPFile(self, filename2proto(path))

    def isfile(self, path):
        logger.debug("isfile: %s", path)
        resp = self._msg_get(protocol.NodeInfoRequest(filename2proto(path)))
        logger.debug("isfile: %s result: %s", path, resp.isfile)
        return resp.isfile

    def isdir(self, path):
        return not self.isfile(path)

    def listdir(self, path='./', wildcard=None, full=False, absolute=False, dirs_only=False, files_only=False):
        logger.debug("listdir: %s", path)
        fn_tuple = filename2proto(path)
        resp = self._msg_get(protocol.DirectoryListRequest(fn_tuple))

        # absolute doesn't make sense without full
        if absolute:
            full = True

        rv = []
        for i in resp.listing:
            if full:
                rvi = proto2filename(fn_tuple + (i,))
            else:
                rvi = i

            if absolute:
                rvi = '/' + rvi
            rv.append(rvi)
        return rv

    def makedir(self, path, recursive=False, allow_recreate=False):
        raise UnsupportedError()

    def remove(self, path):
        raise UnsupportedError()

    def removedir(self, path, recursive=False, force=False):
        raise UnsupportedError()

    def rename(self, src, dst):
        raise UnsupportedError()

    def getinfo(self, path):
        logger.debug("getinfo: %s", path)
        resp = self._msg_get(protocol.NodeInfoRequest(filename2proto(path)))
        ret = {}
        if resp.size: ret['size'] = resp.size
        if resp.created: ret['created_time'] = datetime.fromtimestamp(resp.created)
        if resp.accessed: ret['accessed_time'] = datetime.fromtimestamp(resp.accessed)
        if resp.modified: ret['modified_time'] = datetime.fromtimestamp(resp.modified)
        return ret


class SRFPFile (FileLikeBase):
    def __init__(self, fs, path):
        logger.debug("SRFPFile init: %s", path)
        super(SRFPFile, self).__init__()
        self.path = path
        self.fs = fs
        self.ptr = 0

    def _read(self, sizehint=-1):
        if sizehint == -1 or sizehint > 0x0fff:
            sizehint = 0x0fff
        logger.debug("_read: ptr=%s, s=%s", self.ptr, sizehint)
        rv = self.fs._msg_get(protocol.FileContentsRequest(self.ptr, sizehint, self.path))
        returned_len = len(rv.data)
        if returned_len == 0:
            return None
        self.ptr += returned_len
        return rv.data

    def _seek(self, offset, whence):
        if whence != 0:
            raise NotImplementedError()
        self.ptr = offset

    def _tell(self):
        return self.ptr

class SRFPFSDsStorage (SRFPFS):
    """Provide fake .DS_Store files to keep OS X happy.

    Extends SRFPFS, adding fake .DS_Store entries to every directory in the filesystem,
    and handing out blank StringIO objects when they're open()ed.

    The contents of these objects is lost when they are closed. 

    PyFilesystem doesn't seem to tell the OS that the volume it's mounting is readonly,
    and apparently OS X __really__ doesn't like it when it can't write to .DS_Store files,
    so this gives it something to write to in order to keep it happy.
    """

    def getinfo(self, path):
        if path.endswith(".DS_Store"):
            return {'size': 0}
        else:
            return super(SRFPFSDsStorage, self).getinfo(path)

    def open(self, path, *args, **kwargs):
        if path.endswith(".DS_Store"):
            return StringIO()
        else:
            return super(SRFPFSDsStorage, self).open(path, *args, **kwargs)

    def isfile(self, path):
        if path.endswith(".DS_Store"):
            return True
        else:
            return super(SRFPFSDsStorage, self).isfile(path)

    def isdir(self, path):
        if path.endswith(".DS_Store"):
            return False
        else:
            return super(SRFPFSDsStorage, self).isdir(path)

    def listdir(self, *args, **kwargs):
        rv = super(SRFPFSDsStorage, self).listdir(*args, **kwargs)
        rv.append('.DS_Store')
        return rv


@begin.start
@begin.logging
def start(path, mountpoint):
    myfs = SRFPFSDsStorage(path)
    from fs.expose import fuse
    fuse.mount(myfs, mountpoint.encode('utf8'), foreground=True)
