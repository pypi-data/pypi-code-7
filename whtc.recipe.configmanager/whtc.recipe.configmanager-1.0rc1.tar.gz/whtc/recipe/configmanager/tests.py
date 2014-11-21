"""
Run whtc.recipe.configmanager doc tests
"""
__docformat__ = 'restructuredtext'

import errno
import os
import unittest

import zc.buildout.testing

from zope.testing import doctest, renormalizing

import collective.recipe.template

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def _remove_test_files(test):
    test_path = os.path.join(os.path.dirname(test.filename), 'testdata')
    for name in [
        'OUTPUT.TXT', 
        'TEST_FILE.INI', 
        'TEST_FILE.INI.BK0',
        'TEST_FILE.INI.BK1',
        ]:
            file_path = os.path.join(test_path, name)
            try:
                if os.stat(file_path):
                    os.remove(file_path)
            except OSError, err:
                if err.errno != errno.ENOENT:
                    raise

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install('collective.recipe.template', test)
    zc.buildout.testing.install_develop('whtc.recipe.configmanager', test)

    # Clean up any leftover files...
    _remove_test_files(test)
    
def tearDown(test):
    # Clean up any leftover files...
    _remove_test_files(test)

    zc.buildout.testing.buildoutTearDown(test)

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'README.txt',
                setUp=setUp,
                tearDown=tearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')