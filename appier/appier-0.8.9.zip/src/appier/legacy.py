#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive Appier Framework
# Copyright (C) 2008-2014 Hive Solutions Lda.
#
# This file is part of Hive Appier Framework.
#
# Hive Appier Framework is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive Appier Framework is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive Appier Framework. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2014 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import os
import imp
import sys
import functools

import urllib #@UnusedImport

root = sys.path.pop(0)
try: import urllib2
except ImportError: urllib2 = None
finally: sys.path.insert(0, root)

root = sys.path.pop(0)
try: import urllib.error
except ImportError: urllib.error = None
finally: sys.path.insert(0, root)

root = sys.path.pop(0)
try: import urllib.request
except ImportError: urllib.request = None
finally: sys.path.insert(0, root)

try: import HTMLParser
except ImportError: import html.parser; HTMLParser = html.parser

try: import cPickle
except ImportError: import pickle; cPickle = pickle

try: import cStringIO
except ImportError: import io; cStringIO = io

try: import StringIO as _StringIO
except ImportError: import io; _StringIO = io

try: import urlparse as _urlparse
except ImportError: import urllib.parse; _urlparse = urllib.parse

PYTHON_3 = sys.version_info[0] >= 3
""" Global variable that defines if the current python
interpreter is at least python 3 compliant, this is used
to take some of the conversion decision for runtime """

if PYTHON_3: LONG = int
else: LONG = long #@UndefinedVariable

if PYTHON_3: BYTES = bytes
else: BYTES = str #@UndefinedVariable

if PYTHON_3: UNICODE = str
else: UNICODE = unicode #@UndefinedVariable

if PYTHON_3: OLD_UNICODE = None
else: OLD_UNICODE = unicode #@UndefinedVariable

if PYTHON_3: STRINGS = (str,)
else: STRINGS = (str, unicode) #@UndefinedVariable

if PYTHON_3: INTEGERS = (int,)
else: INTEGERS = (int, long) #@UndefinedVariable

# saves a series of global symbols that are going to be
# used latter for some of the legacy operations
_ord = ord
_chr = chr
_str = str
_bytes = bytes

if PYTHON_3: Request = urllib.request.Request
else: Request = urllib2.Request

if PYTHON_3: HTTPHandler = urllib.request.HTTPHandler
else: HTTPHandler = urllib2.HTTPHandler

if PYTHON_3: HTTPError = urllib.error.HTTPError
else: HTTPError = urllib2.HTTPError

try: _execfile = execfile #@UndefinedVariable
except: _execfile = None

try: _reduce = reduce #@UndefinedVariable
except: _reduce = None

try: _reload = reload #@UndefinedVariable
except: _reload = None

try: _unichr = unichr #@UndefinedVariable
except: _unichr = None

def with_meta(meta, *bases):
    return meta("Class", bases, {})

def eager(iterable):
    if PYTHON_3: return list(iterable)
    return iterable

def iteritems(associative):
    if PYTHON_3: return associative.items()
    return associative.iteritems()

def iterkeys(associative):
    if PYTHON_3: return associative.keys()
    return associative.iterkeys()

def itervalues(associative):
    if PYTHON_3: return associative.values()
    return associative.itervalues()

def items(associative):
    if PYTHON_3: return eager(associative.items())
    return associative.items()

def keys(associative):
    if PYTHON_3: return eager(associative.keys())
    return associative.keys()

def values(associative):
    if PYTHON_3: return eager(associative.values())
    return associative.values()

def xrange(associative):
    if PYTHON_3: return associative.range()
    return associative.xrange()

def range(associative):
    if PYTHON_3: return eager(associative.range())
    return associative.range()

def ord(value):
    if PYTHON_3 and type(value) == int: return value
    return _ord(value)

def chr(value):
    if PYTHON_3: return _bytes([value])
    if type(value) in INTEGERS: return _chr(value)
    return value

def chri(value):
    if PYTHON_3: return value
    if type(value) in INTEGERS: return _chr(value)
    return value

def bytes(value):
    if not PYTHON_3: return value
    if value == None: return value
    if type(value) == _bytes: return value
    return value.encode("latin-1")

def str(value):
    if not PYTHON_3: return value
    if value == None: return value
    if type(value) == _str: return value
    return value.decode("latin-1")

def orderable(value):
    if not PYTHON_3: return value
    return Orderable(value)

def u(value, encoding = "utf-8"):
    if PYTHON_3: return value
    return value.decode(encoding)

def is_str(value):
    return type(value) == _str

def is_unicode(value):
    if PYTHON_3: return type(value) == _str
    else: return type(value) == unicode #@UndefinedVariable

def is_bytes(value):
    if PYTHON_3: return type(value) == _bytes
    else: return type(value) == _str #@UndefinedVariable

def execfile(path, global_vars, local_vars):
    if not PYTHON_3: return _execfile(path, global_vars, local_vars)
    file = open(path)
    try: data = file.read()
    finally: file.close()
    code = compile(data, path, "exec")
    exec(code, global_vars, local_vars)

def walk(path, visit, arg):
    for root, _dirs, _files in os.walk(path):
        names = os.listdir(root)
        visit(arg, root, names)

def reduce(*args, **kwargs):
    if PYTHON_3: return functools.reduce(*args, **kwargs)
    return _reduce(*args, **kwargs)

def reload(*args, **kwargs):
    if PYTHON_3: return imp.reload(*args, **kwargs)
    return _reload(*args, **kwargs)

def unichr(*args, **kwargs):
    if PYTHON_3: return _chr(*args, **kwargs)
    return _unichr(*args, **kwargs)

def urlopen(*args, **kwargs):
    if PYTHON_3: return urllib.request.urlopen(*args, **kwargs)
    else: return urllib2.urlopen(*args, **kwargs) #@UndefinedVariable

def build_opener(*args, **kwargs):
    if PYTHON_3: return urllib.request.build_opener(*args, **kwargs)
    else: return urllib2.build_opener(*args, **kwargs) #@UndefinedVariable

def urlparse(*args, **kwargs):
    return _urlparse.urlparse(*args, **kwargs)

def urlencode(*args, **kwargs):
    if PYTHON_3: return urllib.parse.urlencode(*args, **kwargs)
    else: return urllib.urlencode(*args, **kwargs) #@UndefinedVariable

def quote(*args, **kwargs):
    if PYTHON_3: return urllib.parse.quote(*args, **kwargs)
    else: return urllib.quote(*args, **kwargs) #@UndefinedVariable

def quote_plus(*args, **kwargs):
    if PYTHON_3: return urllib.parse.quote_plus(*args, **kwargs)
    else: return urllib.quote_plus(*args, **kwargs) #@UndefinedVariable

def unquote(*args, **kwargs):
    if PYTHON_3: return urllib.parse.unquote(*args, **kwargs)
    else: return urllib.unquote(*args, **kwargs) #@UndefinedVariable

def unquote_plus(*args, **kwargs):
    if PYTHON_3: return urllib.parse.unquote_plus(*args, **kwargs)
    else: return urllib.unquote_plus(*args, **kwargs) #@UndefinedVariable

def parse_qs(*args, **kwargs):
    if PYTHON_3: return urllib.parse.parse_qs(*args, **kwargs)
    else: return _urlparse.parse_qs(*args, **kwargs) #@UndefinedVariable

def cmp_to_key(*args, **kwargs):
    if PYTHON_3: return dict(key = functools.cmp_to_key(*args, **kwargs)) #@UndefinedVariable
    else: return dict(cmp = args[0])

def StringIO(*args, **kwargs):
    if PYTHON_3: return cStringIO.StringIO(*args, **kwargs)
    else: return _StringIO.StringIO(*args, **kwargs)

def BytesIO(*args, **kwargs):
    if PYTHON_3: return cStringIO.BytesIO(*args, **kwargs)
    else: return cStringIO.StringIO(*args, **kwargs)

class Orderable(tuple):
    """
    Simple tuple type wrapper that provides a simple
    first element ordering, that is compatible with
    both the python 2 and python 3+ infra-structures.
    """

    def __cmp__(self, value):
        return self[0].__cmp__(value[0])

    def __lt__(self, value):
        return self[0].__lt__(value[0])
