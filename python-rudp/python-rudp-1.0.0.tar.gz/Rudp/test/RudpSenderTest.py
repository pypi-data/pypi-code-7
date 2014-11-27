"""
Created on May 12, 2013

@author: saulius
"""
import unittest
import ntpath
from random import randint

from Rudp import RudpSender


class TestSequenceFunctions(unittest.TestCase):
    def testPathExtract(self):
        fileName = "/home/someting/filename.extension"
        extracted = RudpSender.FileSender.processFileName(fileName)
        print str(extracted)
        self.assertEqual(extracted, "filename.extension", "")

        fileName = "filename.extension"
        extracted = RudpSender.FileSender.processFileName(fileName)
        print str(extracted)
        self.assertEqual(extracted, "filename.extension", "")

    def testRandom(self):
        print "Result = " + str(randint(0, 10 - 10))
        print "Result = " + str(randint(0, 10 - 9))
        print "Result = " + str(randint(0, 10 - 8))


if __name__ == '__main__':
    unittest.main()


def processFileName(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
