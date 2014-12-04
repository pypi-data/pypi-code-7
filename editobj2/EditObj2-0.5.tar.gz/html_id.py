# -*- coding: utf-8 -*-

# editor_tk.py
# Copyright (C) 2007-2008 Jean-Baptiste LAMY -- jiba@tuxfamily.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import base64, cerealizer
from cgi import escape as html_escape

def html_escape_arg(s):
  return html_escape(s).replace(u'"', u'&quot;')


def loads(s):
  return cerealizer.loads(base64.decodestring(s))


class Edition(object):
  def __init__(self, root, current = None, parent = None):
    self.root    = root
    self.current = current or root
    self.parent  = parent  or None
    self._id2obj = { 0 : None }
    self._obj2id = { None : 0 }
    
  def edit(self, current, parent):
    self.current = current
    self.parent  = parent
    
  def obj2id(self, obj):
    id = self._obj2id.get(obj)
    if not id:
      id = len(self._obj2id)
      self._obj2id[obj] = id
      self._id2obj[id ] = obj
    return id
  
  def id2obj(self, id):
    return self._id2obj[id]
  
  def dumps(self):
    return base64.encodestring(cerealizer.dumps(self))
  
cerealizer.register(Edition)


