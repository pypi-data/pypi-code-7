# -*- coding: utf-8 -*-

# field_tk.py
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


from editobj2.field import *
from editobj2.field import _RangeField, _ShortEnumField, _LongEnumField
from editobj2.html_id import *

class HtmlField(MultiGUIField):
  def get_edition(self): return self.master.get_edition()
  def get_html(self): pass
  
  def set_html_value(self, value):
    self.set_value(value)
    
    
class HtmlLabelField(HtmlField, LabelField):
  def __init__(self, gui, master, o, attr, undo_stack):
    super(HtmlLabelField, self).__init__(gui, master, o, attr, undo_stack)
    
  def get_html(self):
    return html_escape(unicode(self.get_value()))
  
class HtmlEntryField(HtmlField, EntryField):
  def __init__(self, gui, master, o, attr, undo_stack):
    super(HtmlEntryField, self).__init__(gui, master, o, attr, undo_stack)
    
  def get_html(self):
    return u"""<input name="%s.%s" type="text" value="%s"/>""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), html_escape_arg(unicode(self.get_value())))
  
    
class HtmlFloatField (HtmlEntryField, FloatField):
  def set_html_value(self, value):
    HtmlField.set_value(self, float(value))
  
class HtmlIntField   (HtmlEntryField, IntField):
  def set_html_value(self, value):
    HtmlField.set_value(self, int(value))
  
class HtmlStringField(HtmlEntryField, StringField):
  def set_html_value(self, value):
    HtmlEntryField.set_value(self, value)
    
  def set_html_value(self, value):
    self.set_value(unicode(value, "utf8"))
  

class HtmlPasswordField(HtmlStringField, PasswordField):
  def get_html(self):
    return u"""<input name="%s.%s" type="password" value="%s"/>""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), html_escape_arg(self.getvalue()))




class HtmlEditButtonField(HtmlField, EditButtonField):
  def __init__(self, gui, master, o, attr, undo_stack):
    Tkinter.Button.__init__(self, master, text = editobj2.TRANSLATOR(u"Edit..."), command = self.on_click)
    super(HtmlEditButtonField, self).__init__(gui, master, o, attr, undo_stack)
    self.update()
    
  def update(self):
    self.updating = 1
    try:
      if self.get_value() is None: self.configure(state = "disabled")
      else:                        self.configure(state = "normal")
    finally: self.updating = 0
    
    
class HtmlWithButtonStringField(HtmlField, WithButtonStringField):
  def __init__(self, gui, master, o, attr, undo_stack):
    Tkinter.Frame.__init__(self, master)
    super(HtmlWithButtonStringField, self).__init__(gui, master, o, attr, undo_stack)
    self.string_field.pack(expand = 1, fill = Htmlinter.BOTH, side = Htmlinter.LEFT)
    button = Htmlinter.Button(self, text = editobj2.TRANSLATOR(self.button_text))
    button.bind("<ButtonRelease>", self.on_button)
    button.pack(expand = 0, fill = Htmlinter.BOTH, side = Htmlinter.RIGHT)
    
class HtmlFilenameField(HtmlWithButtonStringField, FilenameField):
  def on_button(self, *args):
    filename = tkFileDialog.askopenfilename()
    if filename:
      self.string_field.set_value(filename)
      self.string_field.update()
    
class HtmlDirnameField(HtmlWithButtonStringField, DirnameField):
  def on_button(self, *args):
    folder = tkFileDialog.askdirectory()
    if folder:
      self.string_field.set_value(folder)
      self.string_field.update()
    
class HtmlURLField(HtmlStringField):
  pass


# class HtmlBoolField(HtmlField, BoolField):
#   def __init__(self, gui, master, o, attr, undo_stack):
#     super(HtmlBoolField, self).__init__(gui, master, o, attr, undo_stack)
    
#   def get_html(self):
#     if self.get_value(): yes_checked = u'checked="on"'; no_checked  = ""
#     else:                no_checked  = u'checked="on"'; yes_checked = ""
    
#     html  = u"""<input name="%s.%s" type="radio" value="1" %s/>%s""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), yes_checked, editobj2.TRANSLATOR("Yes"))
#     html += u"""&nbsp;""" * 4
#     html += u"""<input name="%s.%s" type="radio" value="0" %s/>%s""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), no_checked , editobj2.TRANSLATOR("No" ))
#     return html
  
#   def set_value(self, value):
#     if value == "1": HtmlField.set_value(self, True)
#     else:            HtmlField.set_value(self, False)

class HtmlBoolField(HtmlField, BoolField):
  def __init__(self, gui, master, o, attr, undo_stack):
    super(HtmlBoolField, self).__init__(gui, master, o, attr, undo_stack)
    
  def get_html(self):
    if self.get_value(): checked = 'checked="on"'
    else:                checked = ""
    return u"""
<input name="%s.%s" type="checkbox" %s/>
<input name="%s.%s" type="hidden" value="off"/>
""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), checked, self.get_edition().obj2id(self.o), html_escape(self.attr))
    
    
class HtmlProgressBarField(HtmlField, ProgressBarField):
  def __init__(self, gui, master, o, attr, undo_stack):
    Htmlinter.Label.__init__(self, master)
    super(HtmlProgressBarField, self).__init__(gui, master, o, attr, undo_stack)
    self.update()
    
  def update(self):
    self.updating = 1
    try:
      v = self.get_value()
      if v is introsp.NonConsistent: self["text"] = "???"
      else:                          self["text"] = "%s%%" % int(100 * v)
    finally: self.updating = 0
    

class HtmlTextField(HtmlField, TextField):
  def __init__(self, gui, master, o, attr, undo_stack):
    super(HtmlTextField, self).__init__(gui, master, o, attr, undo_stack)
    
  def get_html(self):
    nb_rows = 2
    for ligne in self.get_value().split("\n"):
      nb_rows += (len(ligne) // 40) + 1
    return u"""<textarea name="%s.%s" rows="%s" cols="40">%s</textarea>""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), nb_rows, html_escape(unicode(self.get_value())))
    
  def set_html_value(self, value):
    self.set_value(unicode(value, "utf8"))
    
class HtmlObjectAttributeField(HtmlField, ObjectAttributeField):
  def __init__(self, gui, master, o, attr, undo_stack):
    Htmlinter.Frame.__init__(self, master)
    super(HtmlObjectAttributeField, self).__init__(gui, master, o, attr, undo_stack)
    self.attribute_pane.pack(expand = 1, fill = Htmlinter.BOTH)
    self.attribute_pane["relief"] = "sunken"
    self.attribute_pane["borderwidth"] = 1
    
class Html_RangeField(HtmlField, _RangeField):
  def __init__(self, gui, master, o, attr, undo_stack, min, max, incr = 1):
    super(Html_RangeField, self).__init__(gui, master, o, attr, undo_stack, min, max, incr)
    if isinstance(min, int) and isinstance(max, int): self.number_type = int
    else:                                             self.number_type = float
    
  def get_html(self):
    return u"""<input name="%s.%s" type="text" value="%s"/>""" % (self.get_edition().obj2id(self.o), html_escape(self.attr), html_escape_arg(unicode(self.get_value())))
  
  def set_html_value(self, value):
    HtmlField.set_value(self, self.number_type(value))
    
    
class Html_ShortEnumField(HtmlField, _ShortEnumField):
  def __init__(self, gui, master, o, attr, undo_stack, choices, value_2_enum = None, enum_2_value = None):
    super(Html_ShortEnumField, self).__init__(gui, master, o, attr, undo_stack, choices, value_2_enum, enum_2_value)
    
  def get_html(self):
    selected_index = self.get_html_value()
    
    html  = u"""<select name="%s.%s">\n""" % (self.get_edition().obj2id(self.o), html_escape(self.attr))
    items = self.choices.items()
    items.sort()
    for k, v in items:
      index = self.choice_2_index[v]
      if index == selected_index: html += u"""<option value="%s" selected="on">%s</option>\n""" % (index, html_escape(unicode(k)))
      else:                       html += u"""<option value="%s">%s</option>\n""" % (index, html_escape(unicode(k)))
    html   += u"""</select>\n"""
    return html
  
  def get_html_value(self):
    return self.choice_2_index[self.get_value()]
  
  def set_html_value(self, value):
    self.set_value(self.choices[self.choice_keys[int(value)]])
    
Html_LongEnumField = Html_ShortEnumField
