# nxpy.core package ----------------------------------------------------------

# Copyright Nicola Musatti 2008 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Helper classes for the implementation of read-only and writable file objects that forward calls
to an actual file object variable.

These smell a lot of statically typed languages and are likely to be removed or changed a lot in a
future release.

"""

from __future__ import absolute_import

import os


class ReadOnlyFileObject(object):
    r"""
    Implement the non modifying portion of the file object protocol by delegating to 
    another file object.
    
    Subclass and override as needed.
    """
    def __init__(self, file_=None):
        r"""Set the delegate file object."""
        self.setFile(file_)

    @property
    def closed(self):
        return self._file.closed

    @property
    def encoding(self):
        return self._file.encoding

    @property
    def mode(self):
        return self._file.mode

    @property
    def name(self):
        return self._file.name

    @property
    def newlines(self):
        return self._file.newlines

    @property
    def softspace(self):
        return self._file.softspace

    def setFile(self, file_):
        r"""Set the delegate file object."""
        self._file = file_
        
    def close(self): 
        self._file.close()

    def flush(self):
        self._file.flush()

    def __iter__(self):
        return self

    def next(self):
        return next(self._file)

    def read(self, size=-1):
        return self._file.read(size)

    def readline(self, size=-1):
        return self._file.readline(size)

    def readlines(self, sizehint=None):
        if sizehint is None:
            return self._file.readlines()
        else:
            return self._file.readlines(sizehint)

    def xreadlines(self):
        return self._file

    def seek(self, offset, whence=os.SEEK_SET):
        return self._file.seek(offset, whence)

    def tell(self):
        return self._file.tell()


class WritableFileObject(ReadOnlyFileObject):
    r"""
    Implement the file object protocol by delegating to another file object.
    
    Subclass and override as needed.
    """
    def __init__(self, file_=None):
        super(WritableFileObject, self).__init__(file_)

    def truncate(self, size=None):
        if size is None:
            self._file.truncate()
        else:
            self._file.truncate(size)

    def write(self, str_):
        self._file.write(str_)

    def writelines(self, sequence):
        self._file.writelines(sequence)


