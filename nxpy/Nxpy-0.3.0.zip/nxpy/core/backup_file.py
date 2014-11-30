# nxpy.core package ----------------------------------------------------------

# Copyright Nicola Musatti 2008 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
A file with automatic backup.

Implement the context manager protocol, so as to be suitable to be used with
the *with* statement. When used in this fashion changes are discarded when an 
exception is thrown.

"""

from __future__ import absolute_import

import os.path
import shutil
import tempfile

import six

import nxpy.core.error
import nxpy.core.file_object


class NotSavedError(Exception):
    r"""Raised when commit or rollback is called on an inactive *BackUpFile*."""


class RemovalError(Exception):
    r"""Raised to signal errors in the removal of backup files."""


class MissingBackupError(Exception):
    r"""raised when a backup file isn't found."""


class BackupFile(nxpy.core.file_object.ReadOnlyFileObject):
    r"""
    Implements a read only file object used to automatically back up a file that has to be
    modified.
    
    """
    _prefix = "_BackupFile"

    MOVE = 1
    COPY = 2
    
    def __init__(self, file_, ext=".BAK", dir=".", mode=COPY):
        r"""
        Prepare to backup *file_*, either a file-like object or a path. 
        
        The backup file will be created in directory *dir* with extension *ext*. If *mode* is 
        *COPY* the original file will be copied to the backup destination; if *mode* is *MOVE* it 
        will be moved there.
        
        """
        super(BackupFile, self).__init__()
        if mode not in ( BackupFile.MOVE, BackupFile.COPY ):
            raise nxpy.core.error.ArgumentError(self.mode + ": Invalid mode")
        if isinstance(file_, six.string_types):
            self._orig_name = file_
            self._orig_file = None
            self._bck_name = os.path.join(dir, self._orig_name) + ext            
        else:
            self._orig_name = None
            self._orig_file = file_
            self._bck_name = tempfile.mktemp(ext, BackupFile._prefix, dir)
        if mode == BackupFile.MOVE and self._orig_name is None:
            raise nxpy.core.error.ArgumentError("Mode can only be MOVE when file_ is a path.")
        self._bck_file = None
        self._mode = mode
        self._on = False
        self._missing = False

    @property
    def name(self):
        r"""The name of the file to be backed up."""
        if self._orig_name is not None:
            return self._orig_name
        else:
            return self._orig_file.name

    def __enter__(self):
        r"""When the controlling *with* statement is entered, create the backup file."""
        self.save()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        r"""
        When the controlling *with* statement is exited normally discard the backup file,
        otherwise restore it to its original place.
        
        """
        if self._on:
            if exc_type is None:
                self.commit()
            else:
                self.rollback()
        return False

    def save(self):
        r"""Create a backup copy of the original file."""
        self.close()
        if self._mode == BackupFile.MOVE:
            try:
                shutil.move(self._orig_name, self._bck_name)
            except:
                self._missing = True
        elif self._mode == BackupFile.COPY:
            try:
                if self._orig_file is None:
                    self._orig_file = open(self._orig_name, "r+")
                    self._tell = self._orig_file.tell()
                else:
                    self._tell = self._orig_file.tell()
                    self._orig_file.seek(0, os.SEEK_SET)
                self._bck_file = open(self._bck_name,"w+")
                shutil.copyfileobj(self._orig_file, self._bck_file, -1)
                self._orig_file.seek(self._tell, os.SEEK_SET)
                self._bck_file.close()
                self._bck_file = None
            except:
                self._missing = True
        self._on = True

    def commit(self):
        r"""Discard the backup, i.e. keep the supposedly modified file."""
        if not self._on:
            raise NotSavedError(self._name + ": File not saved")
        self.close()
        try:
            os.remove(self._bck_name)
        except:
            if not self._missing:
                raise RemovalError("Error removing file " + self._bck_name)
        self._on = False

    def rollback(self):
        r"""Replace the original file with the backup copy."""
        if not self._on:
            raise NotSavedError(self._name + ": File not saved")
        self.close()
        try:
            if self._mode == BackupFile.MOVE:
                shutil.move(self._bck_name, self._orig_name)
            elif self._mode == BackupFile.COPY:
                self._bck_file = open(self._bck_name,"r")
                self._orig_file.seek(0, os.SEEK_SET)
                shutil.copyfileobj(self._bck_file, self._orig_file, -1)
                if self._orig_name is None:
                    self._orig_file.seek(self._tell, os.SEEK_SET)
                else:
                    self._orig_file.close()
                self._bck_file.close()
                self._bck_file = None
                os.remove(self._bck_name)
        except:
            if not self._missing:
                raise MissingBackupError("File " + self._bck_name + 
                        " not found")
            else:
                if os.access(self._orig_name, os.F_OK):
                    os.remove(self._orig_name)
        self._on = False

    BINARY = 3
    TEXT = 4
    
    def open(self, mode=TEXT):
        r"""Open the backup file for reading. *mode* may be either *TEXT* or *BINARY*."""
        if not self._on:
            raise NotSavedError(self._name + ": File not saved")
        if mode == BackupFile.TEXT:
            self._bck_file = open(self._bck_name,"r")
        elif mode == BackupFile.BINARY:
            self._bck_file = open(self._bck_name,"rb")
        self.setFile(self._bck_file)

    def close(self):
        r"""
        Close the backup file and release the corresponding reference.
        
        The backup file may not be reopened.
        
        """
        if self._bck_file:
            self._bck_file.close()
            self._bck_file = None
            self.setFile(None)
