# -*- coding: utf-8 -*-
"""
    tests/sale.py
    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
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
from trytond.tests.test_tryton import POOL, DB_NAME, USER, CONTEXT
from trytond.transaction import Transaction
from trytond.exceptions import UserError
from decimal import Decimal


class TestSale(unittest.TestCase):
    '''
    Test Sale
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('sale_quantity_constraints')

        self.Sale = POOL.get('sale.sale')
        self.Template = POOL.get('product.template')
        self.Product = POOL.get('product.product')
        self.Uom = POOL.get('product.uom')
        self.Company = POOL.get('company.company')
        self.Party = POOL.get('party.party')
        self.Currency = POOL.get('currency.currency')
        self.User = POOL.get('res.user')
        self.Account = POOL.get('account.account')

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = POOL.get('account.account.template')
        Account = POOL.get('account.account')

        account_create_chart = POOL.get(
            'account.create_chart', type="wizard"
        )

        account_template, = AccountTemplate.search(
            [('parent', '=', None)]
        )

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec
        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = POOL.get('account.account')
        Company = POOL.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else None

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = POOL.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def setup_defaults(self):
        """
        Create default records
        """

        with Transaction().set_context(company=None):
            self.company_party, = self.Party.create([{
                'name': 'Test Party 1'
            }])

        self.currency = self.Currency(
            name='Euro', symbol=u'€', code='EUR',
        )
        self.currency.save()
        self.company, = self.Company.create([{
            'party': self.company_party.id,
            'currency': self.currency
        }])

        self.User.write(
            [self.User(USER)], {
                'main_company': self.company.id,
                'company': self.company.id,
            }
        )

        self._create_coa_minimal(company=self.company)
        self.payment_term, = self._create_payment_term()

        self.unit, = self.Uom.search([('symbol', '=', 'u')])

        template, = self.Template.create([{
            'name': 'Test Template 2',
            'type': 'goods',
            'list_price': Decimal('20'),
            'cost_price': Decimal('5'),
            'default_uom': self.unit.id,
            'salable': True,
            'sale_uom': self.unit.id,
            'account_revenue': self._get_account_by_kind('revenue').id
        }])

        self.product, = self.Product.create([{
            'code': 'CODE',
            'template': template.id,
            'order_minimum': 5,
            'order_maximum': 10,
            'order_multiple': 3,
        }])

        self.sale_party, = self.Party.create([{
            'name': 'Test Party'
        }])

        with Transaction().set_context(company=self.company.id):

            self.sale, = self.Sale.create([{
                'party': self.sale_party.id,
                'company': self.company.id,
                'currency': self.currency.id,
                'payment_term': self.payment_term,
            }])

    def test0010_check_constraint_for_sale_line_case1(self):
        """
        Check sale line constraints to make sure

        1. Sale quantity > product order minimum
        2. Sale quantity < product order maximum
        3. Sale quantity is  mulitple of product order multiple

        """
        SaleLine = POOL.get('sale.line')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            self.assertTrue(self.sale.qty_strict_check)

            # 1. Sale quantity (1) < product order minimum (5)
            with self.assertRaises(UserError):
                SaleLine.create([{
                    'sale': self.sale.id,
                    'type': 'line',
                    'quantity': 3,
                    'unit_price': Decimal('10.00'),
                    'description': 'Test Description1',
                    'unit': self.unit,
                    'product': self.product.id
                }])

            # 2. Sale quantity (12) > product order maximum (10)
            with self.assertRaises(UserError):
                SaleLine.create([{
                    'sale': self.sale.id,
                    'type': 'line',
                    'quantity': 12,
                    'unit_price': Decimal('10.00'),
                    'description': 'Test Description1',
                    'unit': self.unit,
                    'product': self.product.id
                }])

            # 3. Sale quantity (8) % product order multiple (3) != 0
            with self.assertRaises(UserError):
                SaleLine.create([{
                    'sale': self.sale.id,
                    'type': 'line',
                    'quantity': 8,
                    'unit_price': Decimal('10.00'),
                    'description': 'Test Description1',
                    'unit': self.unit,
                    'product': self.product.id,
                }])

            # sale line is created successfully since
            # order_minimum < 9 < order_maximum and is multiple of
            # product order muplitple
            SaleLine.create([{
                'sale': self.sale.id,
                'type': 'line',
                'quantity': 9,
                'unit_price': Decimal('10.00'),
                'description': 'Test Description1',
                'unit': self.unit,
                'product': self.product.id
            }])

    def test0020_check_constraint_for_sale_line_case2(self):
        """
        Check sale line constraints when constraint checks are not required

        """
        SaleLine = POOL.get('sale.line')

        with Transaction().start(DB_NAME, USER, context=CONTEXT):
            self.setup_defaults()

            # Ignore constraint checks
            self.sale.qty_strict_check = False
            self.sale.save()

            # No error is being raised in this case

            # 1. Sale quantity (1) < product order minimum (5)
            SaleLine.create([{
                'sale': self.sale.id,
                'type': 'line',
                'quantity': 1,
                'unit_price': Decimal('10.00'),
                'description': 'Test Description1',
                'unit': self.unit,
                'product': self.product.id,
            }])

            # 2. Sale quantity (12) > product order maximum (10)
            SaleLine.create([{
                'sale': self.sale.id,
                'type': 'line',
                'quantity': 12,
                'unit_price': Decimal('10.00'),
                'description': 'Test Description1',
                'unit': self.unit,
                'product': self.product.id,
            }])

            # 3. Sale quantity (8) % product order multiple (3) != 0
            SaleLine.create([{
                'sale': self.sale.id,
                'type': 'line',
                'quantity': 8,
                'unit_price': Decimal('10.00'),
                'description': 'Test Description1',
                'unit': self.unit,
                'product': self.product.id
            }])


def suite():
    """
    Define suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSale)
    )
    return test_suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
