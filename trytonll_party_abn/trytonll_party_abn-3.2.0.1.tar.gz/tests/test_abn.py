# -*- coding: utf-8 -*-
"""
    tests/test_views_depends.py

    :copyright: (C) 2014 by Lava Lab Software Pty Ltd
    :license: BSD, see LICENSE for more details.
"""
import sys
import os
DIR = os.path.abspath(os.path.normpath(os.path.join(
    __file__, '..', '..', '..', '..', '..', 'trytond'
)))
if os.path.isdir(DIR):
    sys.path.insert(0, os.path.dirname(DIR))
import unittest

import trytond.tests.test_tryton
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT


class TestABNValidation(unittest.TestCase):
    '''
    Test the ABN validation
    '''

    def setUp(self):
        """
        Install module before test runs
        """
        trytond.tests.test_tryton.install_module('party_abn')

    def test0010empty_abn_no_validation(self):
        """
        If the abn is not filled, don't bother validating
        """
        Party = POOL.get('party.party')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            party = Party(**{
                'name': 'Party Number 1 with no ABN',
            })
            party.save()

            self.assertTrue(party.id)
            self.assertEqual(party.abn, None)

    def test0020invalid_abn_raises_error(self):
        """
        Ensure that no invalid ABNs get saved
        """
        Party = POOL.get('party.party')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            party = Party(**{
                'name': 'Party Number 2 with bad ABN',
                'abn': '99999999999',
            })
            with self.assertRaises(UserError):
                party.save()

    def test0030valid_abn_works(self):
        """
        It works! when you have a valid ABN
        """
        Party = POOL.get('party.party')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            party = Party(**{
                'name': 'Party Number 3 with good ABN',
                'abn': '53004085616',
            })
            party.save()


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestABNValidation),
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
