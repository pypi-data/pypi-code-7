#!/usr/bin/env python

# Imports #####################################################################
import sys
from os import path, remove
from shutil import copyfile
from time import sleep
import unittest

sys.path.insert(0, path.abspath(path.join(path.dirname(__file__), '..', '..')))
from persistent_pineapple import PersistentPineapple as PP


###############################################################################
class SanityTest(unittest.TestCase):
    test_path = path.dirname(path.realpath(__file__))
    test_file = "test1.json"
    save_file = "save1.json"
    woc_file = "woc1.json"
    fqtest = path.join(test_path, test_file)
    fqsave = path.join(test_path, save_file)
    fqwoc = path.join(test_path, woc_file)

    def test_init(self):
        '''Verify object creation works/fails correctly'''

        # verify error is raised when no file is specified
        self.assertRaises(TypeError, PP)
        self.assertRaises(TypeError, PP, woc=True)
        self.assertRaises(TypeError, PP, woc=False)
        self.assertRaises(TypeError, PP, path=None)

        # verify error is raised if file can't be found
        self.assertRaises((OSError, IOError), PP, self.test_file)
        self.assertRaises((OSError, IOError), PP, self.test_file, woc=True)
        self.assertRaises((OSError, IOError), PP, self.test_file, woc=False)

        # verify valid file creates object
        self.assertTrue(isinstance(PP(self.fqtest), PP))
        self.assertTrue(isinstance(PP(self.fqtest, woc=True), PP))
        self.assertTrue(isinstance(PP(self.fqtest, woc=False), PP))

    def test_get(self):
        '''Verify get method functionality'''
        pp = PP(self.fqtest)
        self.assertEqual(pp.get("setting1"), "value1")
        self.assertEqual(pp.get("setting 2"), 2)
        self.assertEqual(pp.get("section1"), {'subsetting1': 'subvalue2'})

    def test_borg(self):
        '''Verify borg functionality works (simple singleton)'''
        pp1 = PP(self.fqtest, woc=False)
        pp2 = PP(self.fqtest, woc=False)
        pp1.set("unsaved_value", 42)
        self.assertEqual(pp1.get("unsaved_value"), pp2.get("unsaved_value"))

    def test_reload(self):
        '''Verify reload functionality works'''
        pp = PP(self.fqtest, woc=False)
        pp.set("unsaved_value", 42)
        pp.reload()
        self.assertRaises(KeyError, pp.get, "unsaved_value")

    def test_save(self):
        '''Verify save functionality works'''
        pp1 = PP(self.fqtest, woc=False)
        pp1.set("unsaved_value", 42)
        pp1.save(path=self.fqsave)
        pp2 = PP(self.fqsave)
        self.assertEqual(pp1.settings, pp2.settings)
        remove(self.fqsave)

    def test_len(self):
        '''Verify __len__ functionality works'''
        pp = PP(self.fqtest, woc=False)
        len(pp)

    def test_conext(self):
        '''Verify context manager functionality works'''
        pp = PP(self.fqtest, woc=False)

        pp["contex-value-1"] = "one"
        pp["contex-value-2"] = [1, 2, 3]

        before1 = pp["contex-value-1"]
        before2 = pp["contex-value-2"]

        with pp:
            pp["contex-value-1"] = "asdf1234"
            pp["contex-value-2"] = [9, 8, 7, 6]

            self.assertEqual(pp["contex-value-1"], "asdf1234")
            self.assertNotEqual(pp["contex-value-1"], before1)

            self.assertEqual(pp["contex-value-2"], [9, 8, 7, 6])
            self.assertNotEqual(pp["contex-value-2"], before2)

        self.assertEqual(pp["contex-value-1"], before1)
        self.assertEqual(pp["contex-value-2"], before2)

    def test_woc_and_lofc(self):
        '''Verify woc and lofc option functionality works'''
        copyfile(self.fqtest, self.fqwoc)
        copyfile(self.fqtest, self.fqsave)
        pp_orig = PP(self.fqsave, lofc=True)
        pp1 = PP(self.fqwoc, lofc=True)

        pp2 = PP(self.fqwoc, woc=True, lofc=True)
        pp2['woc_value1'] = 1

        del(pp2['woc_value1'])

        pp2.set('woc_value2', 2)
        pp2.save()

        pp1['woc_value2']

        sleep(.1)
        copyfile(self.fqwoc, self.fqsave)
        pp_orig.get('woc_value2')

        remove(self.fqwoc)
        remove(self.fqsave)


###############################################################################
if __name__ == "__main__":
    unittest.main()
