# nxpy.msvs package ----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Manipulation of Microsoft Visual Studio project files.

Currently supports Visual Studio 2008 (9.0) only.

Requires at least Python 2.6

"""

from __future__ import absolute_import

import os.path
import re
import xml.etree.ElementTree

import nxpy.etree.util
import nxpy.msvs.assembly_info


_ns = nxpy.etree.util.Namespace("http://schemas.microsoft.com/developer/msbuild/2003")


class BadProjectFileError(Exception):
    pass


class MissingConfigurationError(Exception):
    pass


class UnknownOutputTypeError(Exception):
    pass


class Reference(object):
    def __init__(self, element):
        self.element = element
        name = element.get("Include")
        i = name.find(",")
        if i != -1:
            self.name = name[0:i]
        else:
            self.name = name
    
    @property
    def hint_path(self):
        return _ns.findtext(self.element, "HintPath")

    def __str__(self):
        s = self.name
        if self.hint_path:
            s = s + "\t" + self.hint_path
        return s


class Satellite(object):
    def __init__(self, name, lang, build_path):
        self.name = name
        self.lang = lang
        self.build_path = build_path
        
    @property
    def target(self):
        return os.path.join(self.build_path, self.lang, self.name)
    
    def __str__(self):
        return self.target


class Project(object):
    _app_conf_re = re.compile(r"[^.]+\.config", re.IGNORECASE)
    
    _emb_res_re = re.compile(r"[^.]+\.([^.]+)\.resx", re.IGNORECASE)
    
    def __init__(self, path):
        self.path = os.path.realpath(path)
        self.dir, name = os.path.split(self.path)
        self.name, self.extension = os.path.splitext(name)
        try:
            self.tree = xml.etree.ElementTree.parse(path)
#            xml.etree.ElementTree.dump(self.tree) 
        except IOError:
            raise BadProjectFileError(path)
        self.root = self.tree.getroot()
        pgs = [ pg for pg in _ns.findall(self.root, "PropertyGroup") ]
        self.configuration = _ns.findtext(pgs[0], "Configuration")
        self.platform = _ns.findtext(pgs[0], "Platform")
        self.output_type = _ns.findtext(pgs[0], "OutputType")
        self.assembly_name = _ns.findtext(pgs[0], "AssemblyName")
        self.assembly_file = self.assembly_name + self._extension()
        for pg in pgs[1:]:
            cond = pg.get("Condition")
            if ( cond and ( cond.find("Configuration") == -1 or 
                            cond.find(self.configuration) != -1 ) and
                          ( cond.find("Platform") == -1 or 
                            cond.find(self.platform) != -1 ) ):
                self.output_path = _ns.findtext(pg, "OutputPath")
                self.assembly_dir = os.path.join(self.dir, self.output_path)
                break
        else:
            raise MissingConfigurationError()
        self.assembly = os.path.join(self.assembly_dir, self.assembly_file)
        self.references = []
        self.sources = []
        self.satellites = []
        self.app_config = None
        self.assembly_info = None
        for ig in _ns.findall(self.root, "ItemGroup"):
            for ref in _ns.findall(ig, "Reference"):
                self.references.append(Reference(ref))
            for tag in ( "ApplicationDefinition", "Page", "Resource" ):
                for src in _ns.findall(ig, tag):
                    self._add_source(src)
            for src in _ns.findall(ig, "Compile"):
                self._add_source(src)
                if src.get("Include").find("AssemblyInfo") != -1:
                    self.assembly_info = nxpy.msvs.assembly_info.AssemblyInfo(
                            os.path.join(self.dir, src.get("Include")))
            for res in _ns.findall(ig, "EmbeddedResource"):
                self._add_source(res)
                match = self._emb_res_re.match(res.get("Include"))
                if match and match.group(1) not in [ l.lang for l in self.satellites ]:
                    self.satellites.append(Satellite(self.assembly_name + ".resources.dll", 
                            match.group(1), self.assembly_dir))
            for f in _ns.findall(ig, "None"):
                match = self._app_conf_re.match(f.get("Include"))
                if match:
                    self._add_source(f)
                    self.app_config = os.path.join(self.assembly_dir, self.assembly_file + 
                            ".config")

    def _add_source(self, src):                
        self.sources.append(os.path.join(self.dir, src.get("Include")))

    def _extension(self):
        t = self.output_type.lower()
        if t == "library":
            return ".dll"
        elif t == "winexe":
            return ".exe"
        else:
            raise UnknownOutputTypeError(self.output_type)
            
    def __str__(self):
        s = ( "Project: " + self.path + "\nConfiguration: " + self.configuration + "\nPlatform: " + 
              self.platform + "\nAssembly: " + self.assembly + "\nVersion: " + 
              self.assembly_info.version + "\nApp.config: " + str(self.app_config) + 
              "\nReferences:" )
        return ( "\n\t".join([ s ] + [ str(r) for r in self.references ]) + 
                 "\n\t".join([ "\nSatellites:" ] + 
                         [ str(sat) for sat in self.satellites ]) + 
                 "\n\t".join([ "\nSources:" ] + [ str(src) for src in self.sources ]) )
