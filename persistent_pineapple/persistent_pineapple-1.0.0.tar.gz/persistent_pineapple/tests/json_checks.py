#!/usr/bin/env python

# Imports #####################################################################
import unittest
import sys

from persistent_pineapple._json import container_to_ascii, JSON


###############################################################################
class SanityTest(unittest.TestCase):

    def test_container_to_ascii(self):
        '''Verify container_to_ascii functionality'''
        self.assertEqual(container_to_ascii(int(4)), 4)
        if sys.version_info[0] == 2:
            orig_list = ['test', unicode('test')]
        else:
            orig_list = ['test', 'test']
        new_list = container_to_ascii(orig_list)
        self.assertEqual(len(orig_list), len(new_list))
        for i in range(len(new_list)):
            if sys.version_info[0] == 2:
                self.assertEqual(new_list[i], orig_list[i].encode('ascii'))
            else:
                self.assertEqual(new_list[i], orig_list[i])

    def test_prep_json_string(self):
        '''Verify _prep_json_string functionality'''
        json = JSON()
        self.assertRaises(ValueError, json._prep_json_string, ',  ,')
        self.assertRaises(ValueError, json._prep_json_string, ':  ,')
        self.assertRaises(ValueError, json._prep_json_string, ']  [')

    def test_load(self):
        '''Verify load functionality'''
        json = JSON()
        # 'Must pass in either string or path'
        self.assertRaises(Exception, json.load)
        self.assertRaises(Exception, json.load)
        # 'Must enter either string or path'
        self.assertRaises(ValueError, json.load, 0, 0)

        self.assertRaises(ValueError, json.load, '{"key1": "value",'
                                                 '\'key2\': "value2"}')
        self.assertRaises(ValueError, json.load, '{key1: 1},')
        self.assertRaises(ValueError, json.load, '{"key1": []},')


###############################################################################
if __name__ == "__main__":
    unittest.main()
