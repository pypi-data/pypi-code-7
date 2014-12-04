#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2007 Jean-Baptiste LAMY -- jiba@tuxfamily.org
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

import sys, os, os.path, editobj2, editobj2.introsp as introsp, editobj2.observe as observe, editobj2.field as field
import editobj2.undoredo as undoredo
import cerealizer

from editobj2.html_cgi import *

class Test(object):
  def __init__(self, nom, age):
    self.nom         = nom
    self.age         = age
    self.language    = u"fr"
    self.cv          = u"Bla bla\nBléa..."
    self.check       = 1
    self.enum        = u"Item3"
    self.enum2       = 3
    self.poids       = 64.0
    
  def __unicode__(self): return self.nom

class Tests(object):
  def __init__(self, l):
    self.children = l
    
  def __unicode__(self): return u"Tests"

cerealizer.register(Test)
cerealizer.register(Tests)

descr = introsp.description(Test)
descr.set_field_for_attr("enum"    , field.EnumField([u"Item1", u"Item2", u"Item3"]))
descr.set_field_for_attr("enum2"   , field.EnumField([1, 2, 3]))
descr.set_field_for_attr("nom", field.StringField)
descr.set_field_for_attr("age", field.StringField)
descr.set_field_for_attr("language", field.StringField)
descr.set_field_for_attr("cv"      , field.TextField)
descr.set_field_for_attr("check"   , field.BoolField)
descr.set_field_for_attr("poids"   , field.RangeField(40.0, 150.0))

descr.set_details(u"Test EditObj2 en HTML")







class My_CGI(EditObj2_CGI):
  def on_new_edition(self):
    test1 = Test("Jiba", 29)
    test2 = Test("Blam", 28)
    tests = Tests([test1, test2])
    
    self.edit(tests)
    self.send_edition()
    
  
  
my_cgi = My_CGI()
my_cgi.run()

