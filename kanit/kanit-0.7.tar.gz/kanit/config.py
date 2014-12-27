#!/usr/bin/python
#
# Kanit config

import sys
import json
import unittest
from StringIO import StringIO

class Config:

    def __init__(self):
        self.status_order = []


    def load(self, io):

        conf = json.load(io)

        self.status_order = conf['status.order']

    def LoadFromFile(self, fname):
        f = open(fname, 'r')
        self.load(f)
        f.close()


class SimpleFileTestCase(unittest.TestCase):
    
    def setUp(self):
        self.contents = """
{
    "status.order": ["Dog", "Cat", "Gold Fish"]
}
"""

    def testStatusOrderLoadedList(self):
        io = StringIO(self.contents)
        conf = Config()
        conf.load(io)
        assert len(conf.status_order) == 3, \
                'Expected status_order with 3 members, got %d' % \
                len(conf.status_order)


    def testStatusOrderMemberOrder(self):
        io = StringIO(self.contents)
        conf = Config()
        conf.load(io)
        assert conf.status_order[0] == 'Dog', \
                'Expected 3rd member to be Dog, got "%s"' % \
                conf.status_order[0]

        assert conf.status_order[1] == 'Cat', \
                'Expected 3rd member to be Cat, got "%s"' % \
                conf.status_order[1]

        assert conf.status_order[2] == 'Gold Fish', \
                'Expected 3rd member to be Gold Fish, got "%s"' % \
                conf.status_order[2]


if __name__ == '__main__':
    unittest.main()
