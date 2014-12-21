#!/usr/bin/python
"""
Tests for `account` module.
"""

from __future__ import print_function

try:
    from ConfigParser import ConfigParser
except:
    # python 3
    from configparser import ConfigParser

import os.path

import pytest
from pysimple import account


@pytest.fixture(scope='module')
def real_account():
    config = ConfigParser()
    config.read('test/login.ini')
    return account.Account(config.get('Credentials', 'username'),
                           config.get('Credentials', 'password'))


@pytest.mark.skipif(not os.path.isfile('test/login.ini'), reason='Need login to test Simple API')
class TestAPI(object):
    """
    The only thing we're really testing is if their API has changed,
    so we gotta *do it live*.

    Need at least one goal, and some transaction history.

    Make sure to add tests for any fields that are used.
    """

    def test_login(self, real_account):
        try:
            real_account.login()
        except:
            pytest.exit('LOGIN FAIL')

    def test_all_goals(self, real_account):
        keys = ['archived', 'name', 'amount', 'id']
        all_goals = real_account.all_goals()
        for key in keys:
            assert key in all_goals[0]

    def test_transactions(self, real_account):
        keys = ['timestamp', 'transactions']
        transactions = real_account.transactions()
        for key in keys:
            assert key in transactions

    def test_balances(self, real_account):
        keys = ['bills', 'deposits', 'safe_to_spend',
                'goals', 'total', 'pending']
        balances = real_account.balances()
        for key in keys:
            assert key in balances

    def test_create_goal(self, real_account):
        pass

    def test_remove_goal(self, real_account):
        pass

    def test_transfer_between_goals(self, real_account):
        pass

    def test_transfer_between_sts(self, real_account):
        pass
