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

import editobj2
from editobj2.editor  import *
from editobj2.html_id import *

class HtmlEditorDialog(EditorDialog):
  def __init__(self, gui, direction = "h", on_validate = None, edit_child_in_self = 1, undo_stack = None, on_close = None):
    super(HtmlEditorDialog, self).__init__(gui, direction, on_validate, edit_child_in_self, undo_stack, on_close)
    
    self.action_url = "XXX"
    
  def edit(self, o, edition = None):
    EditorDialog.edit(self, o)
    self.o = o
    self.edition = edition or Edition(o)
    
  def edit_child(self, o, edition = None):
    EditorDialog.edit_child(self, o)
    self.edition = edition or Edition(o)
    
  def on_cancel(self):
    self.on_validate(None)
    self.destroy()
    
  def on_ok(self):
    self.on_validate(self.editor_pane.attribute_pane.o)
    self.destroy()
    
  def get_html(self):
    return self.editor_pane.get_html()
  
    
class HtmlHEditorPane(HEditorPane):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None):
    super(HtmlHEditorPane, self).__init__(gui, master, edit_child_in_self, undo_stack)
  
  def get_edition(self): return self.master.edition
  
  def get_html(self):
    return u"""
<table style="border-width: 0px; border-style: solid; border-color: rgb(200,200,220); background-color: rgb(200,200,220); "><tr><td>
<table border="0" cellspacing="0">
<tr><td valign="top" style="background-color: rgb(200,200,220); padding-left: 7px; padding-top: 7px; padding-bottom: 7px; padding-right: 0px; width: 20em;">

%s

</td><td valign="top" rowspan="2" style="padding: 7px; padding-left: 14px; background-color: white; ">
<table border="0"><tr><td style="border-bottom-width: 2px; border-bottom-style: solid; border-bottom-color: rgb(200,200,220);">
%s
</td></tr><tr><td style="padding-top: 7px; ">
%s
</td></tr></table>
</td></tr><tr><td valign="bottom" style="padding: 5px; background-color: rgb(200,200,220);">

%s

</td></tr></table>
</td></tr></table>
""" % (self.hierarchy_pane.get_html(), self.icon_pane.get_html(), self.attribute_pane.get_html(), self.childhood_pane.get_html())
    

class HtmlVEditorPane(VEditorPane):
  def __init__(self, gui, master, edit_child_in_self = 1, undo_stack = None):
    super(HtmlVEditorPane, self).__init__(gui, master, edit_child_in_self, undo_stack)

  def get_edition(self): return self.master.edition
  
  def get_html(self):
    return u"""<table style="border-width: 2px; border-style: solid; border-color: rgb(200,200,220);">
<tr><td valign="top" style="background-color: rgb(200,200,220); padding: 7px;">
%s
<br/>
%s
</td></tr><tr><td valign="top">
<table border="0"><tr><td style="border-bottom-width: 2px; border-bottom-style: solid; border-bottom-color: rgb(200,200,220);">
%s
</td></tr><tr><td>
%s
</td></tr></table>
</td></tr></table>
""" % (self.hierarchy_pane.get_html(), self.childhood_pane.get_html(), self.icon_pane.get_html(), self.attribute_pane.get_html())
      

class HtmlIconPane(IconPane):
  def __init__(self, gui, master, use_small_icon = 0, compact = 0, bold_label = 1):
    super(HtmlIconPane, self).__init__(gui, master, use_small_icon, compact, bold_label)
    
  def get_html(self):
    import urllib
    
    return u"""
<img src="%s" style="float: left; padding-right: 1em; padding-top: 1em; padding-bottom: 1em;"/>
<h3 style="text-align: center;">%s</h3>
<p>%s</p>
""" % (
  "?_get_image=%s" % urllib.quote(self.descr.icon_filename_for(self.o), safe = ""),
  html_escape(self.label),
  html_escape(self.details),
  )
  def _set_icon_filename_label_details(self, icon_filename, label, details):
    self.icon_filename = icon_filename
    self.label         = label
    self.details       = details
    
    
class HtmlAttributePane(AttributePane):
  def __init__(self, gui, master, edit_child = None, undo_stack = None, **gui_opts):
    super(HtmlAttributePane, self).__init__(gui, master, edit_child, undo_stack, **gui_opts)
    
  def get_edition(self): return self.master.get_edition()
  
  def get_html(self):
    html  = u"""<table border="0">\n"""
    
    for priority, name, attr, Field in self.attrs:
      field = self.fields[attr]
      if not field: continue
      html += u"""<tr><td>%s</td><td>%s</td><td>%s</td></tr>\n""" % (html_escape(name), field.get_html(), html_escape(field.unit_label))
      
    html += u"""</table>\n"""
    return html
  
  def _new_field(self, attr, name, Field, unit, i):
    field = Field(self.gui, self, self.o, attr, self.undo_stack)
    if unit: field.unit_label = unit_label
    else:    field.unit_label = u""
    return field
    
    

class HtmlChildhoodPane(ChildhoodPane):
  def __init__(self, gui, master, undo_stack = None):
    super(HtmlChildhoodPane, self).__init__(gui, master, undo_stack)
    
    self.master = master
    
  def get_edition(self): return self.master.get_edition()
  
  def get_html(self):
    o = self.get_edition().current
    p = self.get_edition().parent
    actions        = introsp.description(o.__class__).actions_for(o, p)
    parent_actions = introsp.description(p.__class__).actions_for(p)
    
    html  = u"""<table cellspacing="0" border="0" style="margin-left: 1em;"><tr>\n"""
    if(introsp.ACTION_ADD       in actions) or (introsp.ACTION_ADD in parent_actions): html += u"""<td><input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Add"       type="submit" value="[%s]"/></td>\n""" % editobj2.TRANSLATOR(u"Add")
    if introsp.ACTION_REMOVE    in actions: html += u"""<td><input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Remove"    type="submit" value="[%s]"/></td>\n""" % editobj2.TRANSLATOR(u"Remove")
    if introsp.ACTION_MOVE_UP   in actions: html += u"""<td><input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Move up"   type="submit" value="[%s]"/></td>\n""" % editobj2.TRANSLATOR(u"Move up")
    if introsp.ACTION_MOVE_DOWN in actions: html += u"""<td><input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Move down" type="submit" value="[%s]"/></td>\n""" % editobj2.TRANSLATOR(u"Move down")
    
    html += u"""</tr></table>\n"""
    return html
  def get_html(self):
    o = self.get_edition().current
    p = self.get_edition().parent
    actions        = introsp.description(o.__class__).actions_for(o, p)
    parent_actions = introsp.description(p.__class__).actions_for(p)
    
    html  = u""""""
    if(introsp.ACTION_ADD       in actions) or (introsp.ACTION_ADD in parent_actions): html += u"""<input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Add"       type="submit" value="[%s]"/>\n""" % editobj2.TRANSLATOR(u"Add")
    if introsp.ACTION_REMOVE    in actions: html += u"""<input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Remove"    type="submit" value="[%s]"/>\n""" % editobj2.TRANSLATOR(u"Remove")
    if introsp.ACTION_MOVE_UP   in actions: html += u"""<input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Move up"   type="submit" value="[%s]"/>\n""" % editobj2.TRANSLATOR(u"Move up")
    if introsp.ACTION_MOVE_DOWN in actions: html += u"""<input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; color: blue;" name="_do_action_Move down" type="submit" value="[%s]"/>\n""" % editobj2.TRANSLATOR(u"Move down")
    return html


class DynamicNode(object):
  def __init__(self, parent_node):
    self.parent_node = parent_node
    self.tree        = parent_node.tree
    
 
class Html_HierarchyNode(HierarchyNode, DynamicNode):
  def __init__(self, parent_node, o):
    HierarchyNode.__init__(self, parent_node, o)
    
    self.children    = self.create_children()
    
  def get_html(self, depth = 0):
    if self.tree.get_edition().current is self.o: checked = 1
    else:                                         checked = 0

    if isinstance(self.parent_node, HierarchyNode):
      p = self.tree.get_edition().obj2id(self.parent_node.o)
    else:
      p = 0
    o = self.tree.get_edition().obj2id(self.o)
    
    if checked:
      html  = u"""<div style="position: relative; top: -1px; margin-left: %sem;  border-bottom-width: 2px; border-bottom-style: solid; border-bottom-color: rgb(200,200,220);  background-color: white;  padding: 5px; ">""" % (2 * depth - 0.2)
    else:
      html  = u"""<div style="margin-left: %sem;  border-bottom-width: 2px; border-bottom-style: solid; border-bottom-color: rgb(200,200,220); background-color: rgb(230,230,255);  padding: 5px; border-right-width: 1px; border-right-style: solid; border-right-color: rgb(210,210,230);">""" % (2 * depth)
    html += u"""<input style="text-align: left; padding: 0px; margin: 0px; background-color: transparent; border: none; border-width: 0px; color: blue;" name="_edit_%s.%s" type="submit" value="%s"/>""" % (p, o, html_escape_arg(self.descr.label_for(self.o)))
    html += u"</div>"
    return html
  
  def destroy(self): pass
  
  
class HtmlHierarchyPane(HierarchyPane):
  Node = Html_HierarchyNode
  def __init__(self, gui, master, edit_child, undo_stack = None):
    super(HtmlHierarchyPane, self).__init__(gui, master, edit_child, undo_stack)

    self.tree = self

  def get_edition(self):
    return self.master.master.edition
  
  def get_html(self):
    return self.get_node_html(self.root_node)
    
  def get_node_html(self, node, depth = 0):
    html  = u""
    html += node.get_html(depth) + "\n" + "\n".join([self.get_node_html(subnode, depth + 1) for subnode in node.children])
    return html
    





