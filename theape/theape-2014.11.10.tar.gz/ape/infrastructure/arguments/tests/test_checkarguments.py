
# python standard library
import unittest

# third-party
from mock import MagicMock

# the APE
from ape.interface.arguments.arguments import BaseArguments
from ape.interface.arguments.checkarguments import Check, CheckStrategy
from ape.interface.arguments.basestrategy import BaseStrategy

class TestCheck(unittest.TestCase):
    def setUp(self):
        self.args = ['check']
        self.arguments = Check(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        arguments = Check()
        self.assertIsInstance(arguments, BaseArguments)

        # check that the parent is being instantiated
        arguments.args = '--debug check'.split()
        self.assertTrue(arguments.debug)
        return

    def test_configfilenames(self):
        """
        Does it get the list of config-files?
        """
        default = ['ape.ini']
        self.assertEqual(self.arguments.configfiles, default)

        self.arguments.reset()
        filenames = "umma gumma".split()
        self.arguments.args = self.args + filenames
        self.assertEqual(self.arguments.configfiles, filenames)
        return

    def test_modules(self):
        """
        Does it get a list of optional module names?
        """
        self.assertEqual([], self.arguments.modules)

        self.arguments.reset()
        self.arguments.args = self.args + '--module cow -m man'.split()
        self.assertEqual(self.arguments.modules, 'cow man'.split())
        return

    def test_both(self):
        """
        Does it work if you combine modules and config file names?
        """
        self.arguments.args = "check -m big.pig dog war".split()
        self.assertEqual('dog war'.split(), self.arguments.configfiles)
        self.assertEqual(["big.pig"], self.arguments.modules)
        return
# end TestCheck    


class TestCheckStrategy(unittest.TestCase):
    def setUp(self):
        self.build_ape = MagicMock()
        self.strategy = CheckStrategy()
        
        # monkey patch!
        self.strategy.build_ape = self.build_ape
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        strategy = CheckStrategy()
        self.assertIsInstance(strategy, BaseStrategy)
        return

    def test_function(self):
        """
        Does it execute the strategy correctly?
        """
        configfiles = 'alpha beta gamma'.split()
        ape = MagicMock()
        self.build_ape.return_value = None
        args = MagicMock()
        args.configfiles = configfiles

        # ape not buildable (build_ape returned None)
        self.strategy.function(args)
        self.build_ape.assert_called_with(configfiles)
        self.assertEqual(ape.mock_calls, [])

        # ape was built
        self.build_ape.return_value = ape
        self.strategy.function(args)
        ape.check_rep.assert_called_with()
        return

    def test_error_handling(self):
        """
        Does it catch exceptions?
        """
        self.build_ape.side_effect = Exception("arrrrrgh")
        args = MagicMock()
        self.strategy.function(args)
        return
