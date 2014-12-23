"""Proxy SFTP storage. Forward each request to another SFTP server."""

import paramiko

from pysftpserver.abstractstorage import SFTPAbstractServerStorage
from pysftpserver.futimes import futimes


class SFTPServerProxyStorage(SFTPAbstractServerStorage):
    """Proxy SFTP storage.
    Uses a Paramiko client to forward requests to another SFTP server.
    """

    @staticmethod
    def flagsToMode(flags, mode):
        """Convert:
            os module flags and mode -> Paramiko file open mode.
        """
        # TODO implement me!
        pass

    def __init__(self, remote, port=22, user, password):
        # TODO: SSH agent, pk authentication, and so on...
        """Home sweet home.

        Init the transport and then the client.
        """
        transport = paramiko.Transport((remote, port))
        transport.connect(username=user, password=password)

        self.client = paramiko.SFTPClient.from_transport(transport)

    def verify(self, filename):
        """Verify that requested filename is accessible.

        Can always return True in this case.
        """
        return True

    def stat(self, filename, lstat=False, fstat=False):
        """stat, lstat and fstat requests.

        Return a dictionary of stats.
        Filename is an handle in the fstat variant.
        """
        if not lstat and fstat:
            # filename is an handle
            pass
        elif lstat:
            pass
        else:
            pass

        return {

        }

    def setstat(self, filename, attrs, fsetstat=False):
        """setstat and fsetstat requests.

        Filename is an handle in the fstat variant.
        If you're using Python < 3.3,
        you could find useful the futimes file / function.
        """
        pass

    def opendir(self, filename):
        """Return an iterator over the files in filename."""
        return itertools.chain(iter([b'.', b'..']), self.client.listdir(filename))

    def open(self, filename, flags, mode):
        """Return the file handle.

        In Paramiko there are no flags:
        The mode indicates how the file is to be opened:
            'r' for reading,
            'w' for writing (truncating an existing file),
            'a' for appending,
            'r+' for reading/writing,
            'w+' for reading/writing (truncating an existing file),
            'a+' for reading/appending.
            'x' indicates that the operation should only succeed if
                the file was created and did not previously exist.
        """
        paramikoMode = SFTPServerProxyStorage.flagsToMode(flags, mode)
        self.client.open(filename, paramikoMode)

    def mkdir(self, filename, mode):
        """Create directory with given mode."""
        self.client.mkdir(filename, mode)

    def rmdir(self, filename):
        """Remove directory."""
        self.client.rmdir(filename)

    def rm(self, filename):
        """Remove file."""
        self.client.remove(filename)

    def rename(self, oldpath, newpath):
        """Move/rename file."""
        self.client.rename(oldpath, newpath)

    def symlink(self, linkpath, targetpath):
        """Symlink file."""
        self.client.symlink(linkpath, targetpath)

    def readlink(self, filename):
        """Readlink of filename."""
        l = self.client.readlink(filename)
        return l.encode()

    def write(self, handle, off, chunk):
        """Write chunk at offset of handle."""
        pass

    def read(self, handle, off, size):
        """Read from the handle size, starting from offset off."""
        pass

    def close(self, handle):
        """Close the file handle."""
        handle.close()
