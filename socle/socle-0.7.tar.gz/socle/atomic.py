
import os

class AtomicWrite():
    """
    Ensure that files are written in an atomic manner
    """
    def __init__(self, path, mode=0755, uid=None, gid=None):
        self.path = path
        self.mode = mode
        self.uid = uid
        self.gid = gid
        
    def __enter__(self):
        #self.fh = tempfile.NamedTemporaryFile(delete=False)
        self.fh = open(self.path + ".part", "w")
        return self.fh

    def __exit__(self, ty, fh, tb):
        self.fh.close()
        if ty: # Caught exception, just clean up and do nothing
            os.unlink(self.fh.name)
        else:
            os.system("sync")
            if self.uid >= 0 and self.gid >= 0:
                os.chown(self.fh.name, self.uid, self.gid)
            os.chmod(self.fh.name, self.mode)
            os.rename(self.fh.name, self.path)
            os.system("sync")
