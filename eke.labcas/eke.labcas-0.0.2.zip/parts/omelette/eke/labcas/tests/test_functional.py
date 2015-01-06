# encoding: utf-8
# Copyright 2014 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

u'''LabCAS for EKE — functional doctests.'''

import doctest
import unittest2 as unittest
from plone.testing import layered
from eke.labcas.testing import EKE_LABCAS_FUNCTIONAL_TESTING as LAYER

optionFlags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE)

def test_suite():
    return unittest.TestSuite([
        layered(doctest.DocFileSuite('README.rst', package='eke.labcas', optionflags=optionFlags), LAYER),
    ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
