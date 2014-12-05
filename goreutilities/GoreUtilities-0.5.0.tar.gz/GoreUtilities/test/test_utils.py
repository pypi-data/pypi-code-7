'''
Created on Oct 24, 2013
@author: Eugene Yurtsev
'''
import unittest
import numpy as np
from numpy.testing import assert_almost_equal, assert_equal
from GoreUtilities import util

class TestUtil(unittest.TestCase):
    def test_get_tag_value(self):
        """ Tests get_tag_value function. """
        self.assertIsNone(util.get_tag_value('test', pre='PID_', post='_'))

        self.assertEqual(util.get_tag_value('test_tag1_10_', pre='tag1_', post='_'), 10.0)
        self.assertEqual(util.get_tag_value('test_tag1_10.2_', pre='tag1_', post='_', tagtype=float), 10.2)
        self.assertEqual(util.get_tag_value('test_tag1_10.2_', pre='tag1_', post='_', tagtype=str), '10.2')
        self.assertEqual(util.get_tag_value('test_tag1_10.2_', pre='tag1_', post='[_|\.]', tagtype=int), 10)

        self.assertEqual(util.get_tag_value('PID_23.5.txt', pre=r'PID_' , post='(?=_|\.txt)'), 23.5)
        self.assertEqual(util.get_tag_value('PID_23.5_.txt', pre=r'PID_', post='(?=_|\.txt)') , 23.5)
        self.assertEqual(util.get_tag_value('PID_23_5_.txt', pre=r'PID_', post='(?=_|\.txt)') , 23)
        self.assertEqual(util.get_tag_value('PID_23.txt', pre=r'PID_', post='.txt') , 23)

        # Checking list inputs for post
        self.assertEqual(util.get_tag_value('PID_23_5_.txt', pre=r'PID_', post=['_', '.txt']) , 23)
        self.assertEqual(util.get_tag_value('PID_23.5.txt', pre=r'PID_', post=['_', '.txt']) , 23.5)
        self.assertEqual(util.get_tag_value('PID_23.5_blah.txt', pre=r'PID_', post=['_', '.txt']) , 23.5)

if __name__ == '__main__':
    import nose
    nose.runmodule(argv=[__file__,'-vvs','-x'], exit=False)
