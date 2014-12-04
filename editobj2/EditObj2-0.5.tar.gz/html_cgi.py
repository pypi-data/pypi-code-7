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

import sys, os, cgi
import cgitb; cgitb.enable()

import editobj2
import editobj2.field
import editobj2.introsp as introsp
import editobj2.undoredo as undoredo
from editobj2.html_id import *


class EditObj2_CGI(object):
  def __init__(self):
    self.title        = u"EditObj2 CGI"
    self.ok_label     = u"Ok"
    self.introduction = u""
    self.conclusion   = u""
    
  def on_new_edition(self):
    pass
  
  def on_change_edition(self, new_parent, new_current):
    self.edition.edit(new_current, new_parent)
    self.send_edition()
  
  def on_do_action(self, action_name):
    descr = introsp.description(self.edition.current.__class__)
    actions = descr.actions_for(self.edition.current, self.edition.parent)
    for action in actions:
      if action.name == action_name:
        if isinstance(action, introsp.ActionOnAChild):
          descr = introsp.description(self.edition.parent.__class__)
          descr.do_action(action, undoredo.stack, self.edition.parent, self.edition.current)
        else:
          descr.do_action(action, undoredo.stack, self.edition.current)
        break
    else:
      if action_name == "Add":
        descr = introsp.description(self.edition.parent.__class__)
        index = descr.children_of(self.edition.parent).index(self.edition.current) + 1
        actions = descr.actions_for(self.edition.parent)
        for action in actions:
          if action.name == action_name:
            descr.do_action(action, undoredo.stack, self.edition.parent, index)
            break
          
    if action_name == "Remove": # On ne peut plus éditer l'objet en cours car il a été supprimé !
      self.edition.edit(self.edition.root, None)
      
    self.send_edition()
    
  def on_validate(self):
    self.send_edition()
    
    
  def get_edition(self): return self.edition
  
  def edit(self, root, o = None, p = None):
    self.edition = Edition(root, o, p)
    
  def send_edition(self):
    editobj2.GUI = "Html"
    form = editobj2.edit(self.edition.root)
    form.edit_child(self.edition.current, self.edition)
    
    self.send_html(u"""
<form name="editobj2" method="POST" action="%s">
%s
<input name="EDITOBJ2_obj" type="hidden" value="%s"/>
<br/>
<input type="submit" value="%s"/>
</form>
""" % (
  os.path.basename(sys.argv[0]),
  form.get_html(),
  self.edition.dumps(),
  self.ok_label,
  ))
    
  def send_html(self, html):
    print "Content-Type: text/html"     # HTML is following
    print                               # blank line, end of headers
    print "<?xml version='1.0' encoding='UTF-8' standalone='no' ?>"
    print """<html><head><title>%s</title></head><body>""" % self.title.encode("utf8")
    print self.introduction.encode("utf8")
    print html.encode("utf8")
    print self.conclusion.encode("utf8")
    print """</body></html>"""
    
    
  def send_image(self, filename):
    print "Content-Type: image/%s" % filename[filename.rfind(".") + 1:]
    print
    print open(filename).read()
    
  def run(self):
    form = cgi.FieldStorage()
    
    if     form.has_key("_get_image"):
      image_filename = form["_get_image"].value
      if image_filename.endswith(".png") or image_filename.endswith(".jpeg") or image_filename.endswith(".gif"):
        self.send_image(image_filename)
      return
    
    if not form.has_key("EDITOBJ2_obj"):
      self.on_new_edition()
      
    else:
      self.edition = loads(form["EDITOBJ2_obj"].value)
      
      new_current = None
      do_action   = None
      for key in form.keys():
        if   key == "EDITOBJ2_obj": pass
        
        elif key.startswith("_edit_"):
          new_parent, new_current = key[6:].split(".")
          new_parent  = self.edition.id2obj(int(new_parent ))
          new_current = self.edition.id2obj(int(new_current))
          
        elif key.startswith("_do_action_"):
          do_action = key[11:]
        else:
          id, attr = key.split(".", 1)
          o     = self.edition.id2obj(int(id))
          descr = introsp.description(o.__class__)
          Field = descr.field_for_attr(o, attr)
          field = Field("Html", self, o, attr, undoredo.stack)
          
          if isinstance(field, editobj2.field.BoolField):
            if isinstance(form.getvalue(key), list): field.set_value(1)
            else:                                    field.set_value(0)
          else:
            try:    field.set_html_value(form[key].value)
            except: print >> sys.stderr, sys.exc_info()

      if   new_current:
        self.on_change_edition(new_parent, new_current)
      elif do_action:
        self.on_do_action(do_action)
      else:
        self.on_validate()
