
#python standard library
import unittest

# third party
from mock import MagicMock, patch

# the ape
from ape.interface.arguments.listarguments import List, ListStrategy
from ape.interface.arguments.basestrategy import BaseStrategy


class TestList(unittest.TestCase):
    def setUp(self):
        self.args = ['list']
        self.arguments = List(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build correctly?
        """
        arguments = List(args=['list'])

        # inderited default
        self.assertFalse(arguments.pudb)
        return

    def test_modules(self):
        """
        Does it get the list of plugin modules?
        """
        # default to empty list
        self.assertEqual([], self.arguments.modules)

        # positional arguments
        modules = 'ape bat chameleon'.split()
        self.arguments.reset()
        self.arguments.args = self.args + modules
        self.assertEqual(modules, self.arguments.modules)
        return        


class TestListStrategy(unittest.TestCase):
    def setUp(self):
        self.quartermaster = MagicMock()
        ListStrategy.quartermaster = self.quartermaster
        self.strategy = ListStrategy()
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        strategy = ListStrategy()
        
        self.assertIsInstance(strategy, BaseStrategy)
        
        # the mock insertion in SetUp breaks this
        #self.assertIs(strategy.quartermaster, BaseStrategy.quartermaster)
        return

    def test_function(self):
        """
        Does it list the plugins?
        """
        args = MagicMock()

        args.modules = 'a b c'.split()
        self.strategy.function(args)
        self.assertEqual(args.modules, self.quartermaster.external_modules)
        self.quartermaster.list_plugins.assert_called_with()
        return

    def test_try_except(self):
        """
        Does the decorator catch exceptions?
        """
        self.quartermaster.list_plugins.side_effect = Exception("Something Bad")
        self.strategy.function()
        return
