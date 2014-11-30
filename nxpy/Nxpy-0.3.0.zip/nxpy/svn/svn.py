# nxpy.svn package -----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Subversion client wrapper.

Only supports versions 1.6, 1.7 and 1.8, others might work but have not been
tested.
Requires at least Python 2.6.

"""

# Ensures that tests are skipped rather than broken when run with Python 2.5
from __future__ import with_statement
from __future__ import absolute_import
 
import logging
import os
import os.path
import re

import six

import nxpy.command.command
import nxpy.command.option
import nxpy.core.error
import nxpy.core.past
import nxpy.core.temp_file
import nxpy.svn.url

import nxpy.core._impl.log

_log = logging.getLogger(__name__)


class Info(object):
    r"""Represents the output of the ``svn info`` command in a structured way."""
    _outRe = re.compile(r"([^:]+):\s+(.*)")
    
    def __init__(self, out):
        for l in out.split("\n"):
            match = Info._outRe.match(l)
            if match:
                if match.group(1) == "Path":
                    self.path = os.path.realpath(match.group(2))
                elif match.group(1) == "URL":
                    self.url = match.group(2)
                elif match.group(1) == "Repository Root":
                    self.root = match.group(2)
    
    def __str__(self):
        return " - ".join((self.path, str(self.url), self.root))


_config = nxpy.command.option.Config(
        bool_opts = ( "ignore_externals", "parents", "quiet", "summarize", "version" ),
        value_opts = ( "file", "message", "password", "revision", "username", "value" ), 
        mapped_opts = { "ignore_externals" : "--ignore-externals",
                        "value" : "",
                        "version" : "--version" } )
    
class Parser(nxpy.command.option.Parser):
    r"""Allows passing *nxpy.svn.url.Url* instances as arguments to *Svn*'s methods."""
    def __init__(self, command, arguments, options, **defaults):
        super(Parser, self).__init__(_config, command, 
                [ self._pathtostring(a) for a in arguments ], options, **defaults)
    
    def _pathtostring(self, path):
        if isinstance(path, nxpy.svn.url.Url):
            return str(path)
        elif isinstance(path, six.string_types):
            return path
        else:
            raise nxpy.core.error.ArgumentError()
        

class Svn(nxpy.command.command.Command):
    r"""The actual wrapper."""
    def __init__(self, debug=None):
        super(Svn, self).__init__("svn --non-interactive", debug)
        self._version = None
    
    _versionRe = re.compile(r"(\d+)\.(\d+)\.(\d+)")
    
    def version(self):
        op = Parser("", (), {}, version=True)
        out = self.run(op)[0]
        match = Svn._versionRe.search(out)
        version = ( int(match.group(1)), int(match.group(2)), int(match.group(3)))
        return version

    def info(self, *targets):
        op = Parser("info", targets, {})
        out = self.run(op)[0]
        return Info(out)

    def list(self, *targets):
        op = Parser("list", targets, {})
        out = self.run(op)[0]
        return out.split()
    
    def mkdir(self, *targets, **options):
        op = Parser("mkdir", targets, options, parents=False, username="", password="",
                message="\"[" + __name__ + "] Make dir(s) " + ", ".join(targets) + "\"")
        self.run(op)
        
    def status(self, *targets, **options):
        op = Parser("status", targets, options, quiet=True, ignore_externals=True)
        out = self.run(op)[0]
        ignore_externals = options.get('ignore_externals', True)
        res = [ l for l in out.split("\n") 
                if len(l) > 0 and ( not ignore_externals or l[0] != "X" ) ]
        return "".join(res).strip()

    def import_(self, src, dest, debug=None, **options):
        op = Parser("import", ( src, dest ), {}, username="", password="", 
                    message="\"[" + __name__ + "] Import from " + src + "\"")
        self.run(op, debug)

    def checkout(self, src, dest, debug=None, **options):
        op = Parser("checkout", ( src, dest ), options, username="", password="", 
                ignore_externals=True)
        self.run(op, debug)

    def update(self, *targets, **options):
        op = Parser("update", targets, options, ignore_externals=True)
        self.run(op)

    def commit(self, src, debug=None, **options):
        op = Parser("commit", ( src, ), options, username="", password="", 
                    message="\"[" + __name__ + "] Commit from " + src + "\"")
        self.run(op, debug)

    def copy(self, src, dest, debug=None, **options):
        op = Parser("copy", ( src, dest ), options, ignore_externals=True, username="", password="", 
                    message="\"[" + __name__ + "] Copy from " + src + "\"")
        self.run(op, debug)

    def delete(self, *targets, **options):
        debug = options.get("debug")
        op = Parser("delete", targets, options, username="", password="",
                message="\"[" + __name__ + "] Delete " + ", ".join([ str(t) for t in targets ]) + 
                "\"")
        self.run(op, debug)
    
    def propget(self, name, *targets):
        op = Parser("propget", ( name, ) + targets, {})
        out = self.run(op)[0]
        return out.strip()

    _extRe = re.compile(r"([\S]+)\s+(.*)")
    
    def getexternals(self, d):
        out = self.propget("svn:externals", d)
        res = {}
        for l in out.split("\n"):
            match = Svn._extRe.match(l)
            if match:
                res[match.group(1)] = match.group(2)
        return res
    
    def propset(self, name, *targets, **options):
        debug = options.get("debug")
        value = options.get("value")
        if value:
            del options["value"]
            op = Parser("propset", ( name, value ) + targets, options, username="", password="")
        else:
            op = Parser("propset", ( name, ) + targets, options, file="", username="", password="")
        self.run(op, debug)
        
    def setexternals(self, externals, d, username="", password=""):
        nxpy.core.past.enforce_at_least(nxpy.core.past.V_2_6)
        with nxpy.core.temp_file.TempFile(mode="w+", prefix="svn_setexternals") as f:
            for k, v in six.iteritems(externals):
                f.write(k + "\t" + v + "\n")
            f.seek(0, os.SEEK_SET)
            _log.debug(f.read())
            f.close()
            self.propset("svn:externals", d, file=f.name, username=username, password=password)

    def diff(self, *targets, **options):
        op = Parser("diff", targets, options, summarize=False, revision=None)
        out = self.run(op)[0]
        return out

    def cat(self, *targets, **options):
        op = Parser("cat", targets, options, revision=None)
        out = self.run(op)[0]
        return out
