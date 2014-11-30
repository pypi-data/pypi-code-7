# nxpy.maven package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Maven artifacts.

"""

from __future__ import absolute_import

import os.path

import nxpy.etree.util


_ns = nxpy.etree.util.Namespace("http://maven.apache.org/POM/4.0.0")


class Artifact(object):
    def __init__(self, element):
        self._modified = False
        self._groupId = _ns.find(element, "groupId")
        self._artifactId = _ns.find(element, "artifactId")
        self._version = _ns.find(element, "version")
        try:
            self._packaging = _ns.find(element, "packaging").text
        except AttributeError:
            self._packaging = "jar"
        try:
            self._relativePath = os.path.normpath(_ns.find(element, "relativePath").text)
        except AttributeError:
            self._relativePath = None
    
    groupId = nxpy.etree.util.make_property("_groupId")
    artifactId = nxpy.etree.util.make_property("_artifactId")
    version = nxpy.etree.util.make_property("_version")
    
    def qualified_name(self, full=False):
        name = self.groupId + ":" + self.artifactId
        if full:
            name += ":" + self.packaging + ":" + self.version
        return name

    @property
    def modified(self):
        return self._modified

    @property
    def packaging(self):
        return self._packaging
    
    @property
    def relativePath(self):
        return self._relativePath
    
    def __str__(self):
        return "%s:%s:%s" % ( self.groupId, self.artifactId, self.version )
