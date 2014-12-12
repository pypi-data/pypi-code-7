#!/usr/bin/env python
# vim:fenc=utf-8:tw=77:ts=2:
#
# by Pablo Abelenda (pablo.abelenda@lambdastream.com)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
############################################################################# 


import unittest
import pyncomings
from pyncomings.dao import DAOsqlite3
from pyncomings.parsers import *
from xmldict.xmldict import *

import sqlite3

class testPyncomings(unittest.TestCase):

  """
  A test class for the Pyncomings software.
  """

  def setUp(self):
    """
    set up data used in the tests.
    setUp is called before each test function execution.
    """
    global e1
    global e2
    global search_result
    global query_result_e2_after_modification

    e1 = {'purged_date': 'e1', 'registration_date': 'e1', 'retention_days': 1, 'source': 'e1', 'user': 'e1', 'path': 'e1', 'size': 'e1'}
    e2 = {'purged_date': 'e2', 'registration_date': 'e2', 'retention_days': 2, 'source': 'e2', 'user': 'e2', 'path': 'e2', 'size': 'e2'}

    search_result = [{'purged_date': u'e1', 'registration_date': u'e1', 'retention_days': 1.0, 'source': u'e1', 'user': u'e1', 'path': u'e1', 'size': u'e1'}]
    query_result_e2_after_modification = {'purged_date': u'e2', 'registration_date': u'e2', 'retention_days': 2.0, 'source': u'e2', 'user': u'e2', 'path': u'e2', 'size': u'SIZE22'}

   
  def test_simple(self):
    """
    This test run, at least one time, all the functions defined in the module
    """
    global e1
    global e2
    global search_result
    global query_result_e2_after_modification

    d = DAOsqlite3.DAOEntry(":memory:")
    d.create_table()

    print "Getting a non existing entry, expected None as answer"
    self.assertEqual(d.get_entry(e1["path"]), None)

    print "Updating a non existing entry. Non error expected"
    d.update_entry(e1)
    
    print "Getting all entries. At this point, no one."
    self.assertEqual(d.get_entries(), [])

    print "Getting all entries passing an offset parameter. Exception expected."
    # self.assertRaises(d.get_entries(42))
    try:
        d.get_entries(42)
    except:
        NotImplementedError
    
    print "Creating a new entry -> e1"
    d.create_entry(e1)
    try:
      d.create_entry(e1)
      print "Error, can enter a entry with a path entry previously."
    except sqlite3.IntegrityError:
      print "OK: Integrity error success"

    print "Creating a new entry -> e2"
    d.create_entry(e2)

    print "Getting entries. At this point, e1 and e2, so, not None"
    self.assertNotEqual(d.get_entries(), None)

    print "Checking entry e1"
    self.assertEqual(d.get_entry(e1["path"]), e1)

    print "Checking entry e2"
    self.assertEqual(d.get_entry(e2["path"]), e2)

    print "Searching entries with 'registration_date' equal to e1 - only e1"
    self.assertEqual(d.search_entry_by_date(e1["registration_date"]),search_result)

    print "Copying e2 into e22 and changing e22 size"
    e22 = e2
    e22["size"]="SIZE22"
    d.update_entry(e22)

    print "Getting new entry e22"
    self.assertEqual(d.get_entry(e22["path"]), query_result_e2_after_modification)

    print "Deleting e1 entry"
    d.delete_entry(e1["path"])
    print "Getting e1 after deletion. None expected"
    self.assertEqual(d.get_entry(e1["path"]), None)


def suite():

    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testPyncomings))
    return suite

if __name__ == '__main__':

    unittest.main()

    unittest.TextTestRunner(verbosity=2).run(suite())

  
