# nxpy.msvs package ----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
A C# or Visual Basic.NET source file that conventionally contains information about its containing 
assembly, such as its version number.

"""

from __future__ import absolute_import

import encodings.utf_8_sig
import logging
import os.path
import re

import six

import nxpy.core.backup_file
import nxpy.core.file

import nxpy.core._impl.log


_log = logging.getLogger(__name__)


class BadFileExtensionError(Exception):
    r"Raised when an unknown file extension is found"


class _LineRep(object):
    def __init__(self, start, ai):
        self._start = start
        self._ai = ai
        self.found = -1

    def __call__(self, match):
        _log.debug("ai: " + str(match.start()) + " cm: " + str(self._start))
        if self._start > -1 and match.start() > self._start:
            return match.group(0)
        if match.group(3) == "AssemblyVersion":
            s = self._ai._version
            self.found = 0
        elif match.group(3) == "AssemblyFileVersion":
            s = self._ai._file_version
            self.found = 1
        elif match.group(3) == "AssemblyInformationalVersion":
            s = self._ai._product_version
            self.found = 2
        else:
            return match.group(0)
        return ( match.group(1) + match.group(2) + match.group(3) + "(\"" + s + "\")" + 
                match.group(5) )

        
class AssemblyInfo(object):
    _ai_re = re.compile(r"([<[])([Aa]ssembly:\s+)(\w+)\(\"([^\"]+)\"\)([>\]])")
    _cm_re = re.compile(r"(?:')|(?://)|(/\*)")
    
    def __init__(self, path):
        self.path = path
        self._ext = os.path.splitext(path)[1].lower()
        self._version = None
        self._file_version = None
        self._product_version = None
        self._modified = False 
        comment = False
        ebc = -1
        for l in nxpy.core.file.open_(path, "r", encoding="utf-8"):
            if comment:
                ebc = l.find("*/")
            if not comment or ebc != -1:
                ai_match = self._ai_re.search(l)
                cm_match = self._cm_re.search(l)
                if ai_match and ( ( comment and ebc < ai_match.start() ) or ( not cm_match or 
                        ai_match.start() < cm_match.start() ) ):
                    _log.debug("ai: " + str(ai_match.start()) + " cm: " + 
                            str(cm_match.start() if cm_match else -1))
                    if ai_match.group(3) == "AssemblyVersion":
                        self._version = ai_match.group(4)
                    elif ai_match.group(3) == "AssemblyFileVersion":
                        self._file_version = ai_match.group(4)
                    elif ai_match.group(3) == "AssemblyInformationalVersion":
                        self._product_version = ai_match.group(4)
                if cm_match and cm_match.group(1) and ebc < cm_match.start(1):
                    comment = True
                elif ebc != -1:
                    comment = False
                    ebc = -1

    def _get_version(self):
        return self._version
    def _set_version(self, v):
        self._version = v
        self._modified = True
    version = property(_get_version, _set_version)

    def _get_file_version(self):
        return self._file_version
    def _set_file_version(self, v):
        self._file_version = v
        self._modified = True
    file_version = property(_get_file_version, _set_file_version)

    def _get_product_version(self):
        return self._product_version
    def _set_product_version(self, v):
        self._product_version = v
        self._modified = True
    product_version = property(_get_product_version, _set_product_version)

    def _attr_fmt(self):
        if self._ext == ".vb":
            return r'<Assembly: %s("%s")>'
        elif self._ext == ".cs":
            return r'[assembly: %s("%s")]'
        else:
            raise BadFileExtensionError(self._ext)

    def write(self, dest):
        src = None
        bck = None
        if not dest:
            dest = self.path
            bck = nxpy.core.backup_file.BackupFile(self.path, 
                    mode=nxpy.core.backup_file.BackupFile.MOVE)
            bck.save()
            bck.open(mode=nxpy.core.backup_file.BackupFile.BINARY)
            src = encodings.utf_8_sig.StreamReader(bck)
        else:
            src = encodings.utf_8_sig.StreamReader(open(self.path, "rb"))
        if isinstance(dest, six.string_types):
            dest = encodings.utf_8_sig.StreamWriter(open(dest, "wb+"))
        else:
            dest = encodings.utf_8_sig.StreamWriter(dest)
            dest.seek(0)
        try:
            comment = False
            ebc = -1
            found = [ False, False, False ]
            for l in src:
                if comment:
                    ebc = l.find("*/")
                if not comment or ebc != -1:
                    cm_match = self._cm_re.search(l)
                    lr = _LineRep(cm_match.start() if cm_match else -1, self)
                    l = self._ai_re.sub(lr, l)
                    if lr.found != -1:
                        found[lr.found] = True
                    if cm_match and cm_match.group(1) and ebc < cm_match.start(1):
                        comment = True
                    elif ebc != -1:
                            comment = False
                            ebc = -1
                dest.write(l)
            if not found[0]:
                dest.write(self._attr_fmt() % ( "AssemblyVersion", self.version ))
            if not found[1]:
                dest.write(self._attr_fmt() % ( "AssemblyFileVersion", self.file_version ))
            if not found[2]:
                dest.write(self._attr_fmt() % ( "AssemblyInformationalVersion", 
                        self.product_version ))
            if bck:
                bck.commit()
        except:
            if bck:
                bck.rollback()
            raise
        finally:
            dest.close()

    def save(self):
        if self._modified:
            self.write(None)
            return True
        return False
