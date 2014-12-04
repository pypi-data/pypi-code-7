# -*- coding: utf-8 -*-

# A login dialog box

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

class Test(object):
  def __init__(self, nom, age):
    self.nom         = nom
    self.age         = age
    self.language    = "fr"
    
  def __unicode__(self): return self.nom

class Tests(object):
  def __init__(self, l):
    self.children = l
    
  def __unicode__(self): return "Tests"

cerealizer.register(Test)
cerealizer.register(Tests)

descr = introsp.description(Test)
descr.set_field_for_attr("nom", field.StringField)
descr.set_field_for_attr("age", field.StringField)
descr.set_field_for_attr("language", field.StringField)

descr.set_details(u"Test EditObj2 en HTML")



test1 = Test("Jiba", 29)
test2 = Test("Blam", 28)

tests = Tests([test1, test2])

editobj2.GUI = "Html"

form = editobj2.edit(tests)

s = form.get_html()

print s

open("/tmp/t.html", "w").write(s)
