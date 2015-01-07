# -*- coding: utf-8 -*-
import doctest
import os
import unittest
from plone.testing import layered
from experimental.globalgopipindex.testing import \
    GOPIPINDEX_INTEGRATION_TESTING


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(os.path.join(os.pardir, os.pardir,
                                                  os.pardir, os.pardir,
                                                  'README.rst')),
                layer=GOPIPINDEX_INTEGRATION_TESTING)
    ])
    return suite
