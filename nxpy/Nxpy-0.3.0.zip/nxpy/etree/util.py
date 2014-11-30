# nxpy.etree package ---------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
ElemenTree related utility classes and functions.

Requires at least Python 2.6. Simple import breaks on Python 2.5

"""
from __future__ import absolute_import

import collections
import re
import xml.etree.ElementTree

import six

import nxpy.core.error
import nxpy.core.past

nxpy.core.past.enforce_at_least(nxpy.core.past.V_2_6)


def make_property(elem, key=None):
    r"""
    Creates a property on the text of element 'elem' or, if the 'key' argument is given, on its
    'key' attribute.
    
    """
    if key:
        def _get(self):
            return getattr(self, elem).get(key)
        def _set(self, value):
            getattr(self, elem).set(key, value)
            self._modified = True
        return property(_get, _set)
    else:
        def _get(self):
            return getattr(self, elem).text
        def _set(self, value):
            getattr(self, elem).text = value
            self._modified = True
        return property(_get, _set)


class QName(object):
    r"""Represents a qualified name"""

    _re = re.compile(r"\{(.*)\}(.*)")
    
    def __init__(self, tag):
        m = QName._re.match(tag)
        self.url = m.group(1)
        self.tag = m.group(2)
        
    @property
    def text(self):
        t = []
        if len(self.url) != 0:
            t.append("{{{0}}}".format(self.url))
        t.append(self.tag)
        return "".join(t)
    
    def __str__(self):
        return self.text()
    
        
class Namespace(object):
    r"""
    Represents an XML namespace and provides several utility functions that help handle a
    document without namespace tags.
    
    """
    def __init__(self, url="", element=None):
        if len(url) > 0 and element is not None:
            raise nxpy.core.error.ArgumentError(
                    "Only one between url and element should be specified")
        if element is not None:
            url = QName(element.tag).url
        self.url = url
        self.nspace = "{" + url + "}" if len(url) != 0 else ""

    def find(self, element, tag):
        return element.find(self.nspace + tag)

    def findall(self, element, tag):
        return element.findall(self.nspace + tag)

    def findtext(self, element, tag, default=None):
        return element.findtext(self.nspace + tag, default)
    
    def get_tag(self, element):
        return element.tag[len(self.nspace):-1]
    
    def Element(self, tag, attrib={}, **extra):
        return xml.etree.ElementTree.Element(self.nspace + tag, attrib, **extra)
    
    def SubElement(self, parent, tag, attrib={}, **extra):
        return xml.etree.ElementTree.SubElement(parent, self.nspace + tag, attrib, **extra)


class ContainerElementMixin(Namespace):
    def __init__(self, parent, root_tag, namespace=""):
        super(ContainerElementMixin, self).__init__(namespace)
        self.parent = parent
        self.root_tag = root_tag
        self.root = self.find(self.parent, self.root_tag)
        self.modified = False

    def __len__(self):
        if self.root is None:
            return 0
#        return len(self.root.getchildren())
        return len(self.root)


class MappingElementIterator(collections.Iterator):
    def __init__(self, element):
        self.element = element
        self.iter = element.getchildren().iter()
        
    def next(self):
        return self.element.get_tag(next(self.iter))

        
class MappingElement(ContainerElementMixin, collections.MutableMapping):
    def __init__(self, parent, root_tag, namespace=""):
        ContainerElementMixin.__init__(self, parent, root_tag, namespace)

    def __getitem__(self, key):
        if self.root is None:
            raise KeyError()
        elem = self.root.find(key)
        if elem is None:
            raise KeyError()
        return elem.text
    
    def __setitem__(self, key, value):
        if self.root is None:
            self.root = self.SubElement(self.parent, self.root_tag)
        elem = self.root.find(key)
        if elem is None:
            elem = self.SubElement(self.root, key)
        self.modified = True
        elem.text = value

    def __delitem__(self, key):
        if self.root is None:
            raise KeyError()
        elem = self.root.find(key)
        if elem is None:
            raise KeyError()
        self.modified = True
        self.root.remove(elem)

    def __iter__(self):
        return MappingElementIterator(self)


class SequenceElement(ContainerElementMixin, collections.MutableSequence):
    def __init__(self, parent, root_tag, element_tag, namespace=""):
        ContainerElementMixin.__init__(self, parent, root_tag, namespace)
        self.element_tag = element_tag

    def __getitem__(self, index):
        if self.root is None:
            raise IndexError()
        return self.root[index].text
    
    def __setitem__(self, index, value):
        if self.root is None:
            self.root = self.SubElement(self.parent, self.root_tag)
        elem = None
        try:
            elem = self.root[index]
        except IndexError:
            elem = self.SubElement(self.root, self.element_tag)
        elem.text = value
        self.modified = True
    
    def __delitem__(self, index):
        if self.root is None:
            raise IndexError()
        del self.root[index]
        self.modified = True

    def insert(self, index, value):
        if self.root is None:
            self.root = self.SubElement(self.parent, self.root_tag)
        elem = self.Element(self.element_tag)
        elem.text = value
        self.root.insert(index, elem)
        self.modified = True


class Writer(object):
    _name_re = re.compile(r"<([^\s]+)")
    _tag_re = re.compile(r"(</?)[^:]+:((:?[^>]+>)|(:?[^/]+/>))")

    def __init__(self, root_tag, attributes=None, tab_size=0):
        self.root_tag = root_tag
        self.tab_size = tab_size
        self.attributes = attributes
        self.name = self._name_re.search(self.root_tag).group(1)
        self._root_re = re.compile(r"(<" + self.name + r"[^>]+>)")

    def write(self, node, where):
        if isinstance(where, six.string_types):
            f = open(where, "w+")
        else:
            f = where
        try:
            s = None
            if nxpy.core.past.V_2_7.at_most():
                s = xml.etree.ElementTree.tostring(node)
            else:
                s = xml.etree.ElementTree.tostring(node, encoding="unicode")
            s = self._tag_re.sub(r"\1\2", s)
            s = self._root_re.sub(self.root_tag, s, 1)
            if self.tab_size > 0:
                s = s.replace("\t", " " * self.tab_size)
            if self.attributes is not None:
                d = ( '<?xml version="' + self.attributes.get("version", "1.0") + 
                        '" encoding="' + self.attributes.get("encoding", "UTF-8") + '"')
                if "standalone" in self.attributes:
                    d += ' standalone="' + self.attributes["standalone"] + '"'
                d += "?>\n"
                f.write(d)
            f.write(s)
            f.write("\n\n")
        finally:
            f.close()
