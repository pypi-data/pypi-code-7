# nxpy.maven package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Manipulation of Maven POM files.

"""

from __future__ import absolute_import

import os.path
import xml.etree.ElementTree

import nxpy.etree.util
import nxpy.maven.artifact


_ns = nxpy.etree.util.Namespace("http://maven.apache.org/POM/4.0.0")


class BadPomFileError(EnvironmentError):
    pass


class Dependencies(object):
    def __init__(self, element):
        self.element = element
        self.dependencies = {}
        if self.element is not None:
            for d in element.getchildren():
                a = nxpy.maven.artifact.Artifact(d)
                self.dependencies[a.artifactId] = a

    def _saved(self):
        for a in self.dependencies.values():
            a._modified = False

    @property
    def modified(self):
        return any([ a._modified for a in self.dependencies.values() ])
    
    def contains(self, artifact):
        if isinstance(artifact, nxpy.maven.artifact.Artifact):
            group_id = artifact.groupId
            artifact_id = artifact.artifactId
        else:
            group_id, artifact_id = artifact.split(":")[0:2]
        for a in self.dependencies.values():
            if a.groupId == group_id and a.artifactId == artifact_id:
                return a
        return None
            
    def __str__(self):
        return "\n".join([ str(a) for a in self.dependencies.values() ])


class Scm(object):
    def __init__(self, element):
        self._modified = False
        self.element = element
        self._connection = _ns.find(element, "connection")
        self._developerConnection = _ns.find(element, "developerConnection")
        self._url = _ns.find(element, "url")
    
    connection = nxpy.etree.util.make_property("_connection")
    developerConnection = nxpy.etree.util.make_property("_developerConnection")
    url = nxpy.etree.util.make_property("_url")

    @property
    def modified(self):
        return self._modified


class Repository(object):
    def __init__(self, element):
        self._modified = False
        self.element = element
        self._id = _ns.find(element, "id")
        self._name = _ns.find(element, "name")
        self._url = _ns.find(element, "url")

    id = nxpy.etree.util.make_property("_id")
    name = nxpy.etree.util.make_property("_name")
    url = nxpy.etree.util.make_property("_url")

    @property
    def modified(self):
        return self._modified


class DistributionManagement(object):
    def __init__(self, element):
        self.element = element
        self.repository = Repository(_ns.find(element, "repository"))
        self.snapshotRepository = Repository(_ns.find(element, "snapshotRepository"))

    def _saved(self):
        self.repository._modified = False
        self.snapshotRepository._modified = False

    @property
    def modified(self):
        return self.repository.modified or self.snapshotRepository.modified
    
    
class Properties(nxpy.etree.util.MappingElement):
    def __init__(self, parent):
        super(Properties, self).__init__(parent, "properties", _ns.url)
        
    
class Pom(object):
    _root = ( r'<project xmlns="http://maven.apache.org/POM/4.0.0"'
              r' xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n' 
              r'    xsi:schemaLocation="http://maven.apache.org/POM/4.0.0' 
              r' http://maven.apache.org/maven-v4_0_0.xsd">' )

    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.dir = os.path.split(self.path)[0]
        try:
            self.tree = xml.etree.ElementTree.parse(path)
        except IOError:
            raise BadPomFileError(path)
        self.root = self.tree.getroot()
        self.artifact = nxpy.maven.artifact.Artifact(self.root)
        self.dependencies = Dependencies(_ns.find(self.root, "dependencies"))
        parent = _ns.find(self.root, "parent")
        try:
            self.parent = nxpy.maven.artifact.Artifact(parent)
        except AttributeError:
            self.parent = None
        self.scm = None
        scm = _ns.find(self.root, "scm")
        if scm  is not None:
            self.scm = Scm(scm)
        self.modules = []
        depmgmt = None
        if self.artifact.packaging == "pom":
            modules = _ns.find(self.root, "modules")
            if modules is not None:
                for m in modules.getchildren():
                    self.modules.append(m.text)
            deps = _ns.find(self.root, "dependencyManagement")
            if deps is not None:
                depmgmt = _ns.find(deps, "dependencies")
        self.dependencyManagement = Dependencies(depmgmt)
        self.properties = nxpy.etree.util.MappingElement(self.root, "properties")
        self.assembly_descriptor = None
        build = _ns.find(self.root, "build")
        if build is not None:
            plugins = _ns.find(build, "plugins")
            if plugins is not None:
                for p in plugins.getchildren():
                    if _ns.find(p, "artifactId").text == "maven-assembly-plugin":
                        ad = _ns.find(_ns.find(p, "configuration"), "descriptors")[0]
                        self.assembly_descriptor = os.path.normpath(os.path.join(self.dir, 
                                ad.text))
                        break
        self.distributionManagement = None
        dm = _ns.find(self.root, "distributionManagement")
        if dm is not None:
            self.distributionManagement = DistributionManagement(dm)
        self._writer = nxpy.etree.util.Writer(self._root, None, 4)

    def qualified_name(self, full=False):
        return self.artifact.qualified_name(full)

    @property
    def modified(self):
        return ( self.artifact.modified or ( self.parent and self.parent.modified ) or 
                 self.dependencies.modified or self.dependencyManagement.modified or 
                 ( self.scm and self.scm.modified ) or self.properties.modified or 
                 ( self.distributionManagement and self.distributionManagement.modified ) )

    def write(self, where):
        if not where:
            where = self.path
        self._writer.write(self.root, where)

    def save(self):
        if self.modified:
            self.write(None)
            self.artifact._modified = False
            if self.parent:
                self.parent._modified = False
            self.scm._modified = False
            self.dependencies._saved()
            self.dependencyManagement._saved()
            self.distributionManagement._saved()
            self.properties.modified = False
            return True
        return False
