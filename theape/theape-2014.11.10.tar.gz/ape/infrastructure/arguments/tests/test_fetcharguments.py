
# python standard library
import unittest

# third-party
from mock import MagicMock

# the ape
from ape.interface.arguments.fetcharguments import Fetch, FetchStrategy
from ape.interface.arguments.basestrategy import BaseStrategy
import ape.interface.arguments.fetcharguments


fetch_usage = ape.interface.arguments.fetcharguments.__doc__
class TestFetchArguments(unittest.TestCase):
    def setUp(self):
        self.args = ['fetch']
        self.arguments = Fetch(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        arguments = Fetch(args=['fetch'])

        # test inheritance
        self.assertFalse(arguments.debug)
        self.assertEqual(fetch_usage, arguments.sub_usage)
        return

    def test_names(self):
        """
        Does it get the list of plugin names?
        """
        # default
        self.assertEqual(['Ape'], self.arguments.names)

        # positionl arguments
        self.arguments.reset()
        names = "apple banana cat".split()
        self.arguments.args = self.args + names
        self.assertEqual(names, self.arguments.names)
        return

    def test_modules(self):
        """
        Does it get a list of external modules?
        """
        # default is None
        self.assertEqual([], self.arguments.modules)

        # add one
        self.arguments.reset()
        modules = ['aoeu']
        options = ['-m'] + modules
        self.arguments.args = self.args + options
        self.assertEqual(modules, self.arguments.modules)

        # add multiple
        self.arguments.reset()
        modules = 'a b c d e'.split()
        options = ['-m'] + " -m".join(modules).split()
        self.arguments.args = self.args + options
        self.assertEqual(modules, self.arguments.modules)
        return

    def test_both(self):
        """
        Can you use both names and modules?
        """
        names = 'ab cd'.split()
        modules = 'a b c d'.split()
        arguments_options = names + ['-m'] + ' -m'.join(modules).split()
        self.arguments.args = self.args + arguments_options
        self.assertEqual(names, self.arguments.names)
        self.assertEqual(modules, self.arguments.modules)
        return
# end TestFetchArguments    


class TestFetchStrategy(unittest.TestCase):
    def setUp(self):
        self.quartermaster = MagicMock()
        FetchStrategy.quartemaster = self.quartermaster
        self.strategy = FetchStrategy()
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        strategy = FetchStrategy()
        self.assertIsInstance(strategy, BaseStrategy)
        return

    def test_function(self):
        """
        Does it implement the `fetch` strategy? 
        """
        self.strategy.quartermaster = self.quartermaster
        args = MagicMock()
        args.names = 'a b c'.split()
        args.modules = 'd e f'.split()
        definition_a, definition_b, definition_c = MagicMock(), MagicMock(), MagicMock()
        definitions = [definition_a, definition_b, definition_c]
        plugin_a, plugin_b, plugin_c = MagicMock(), MagicMock(), MagicMock()
        definition_a.return_value = plugin_a
        definition_b.return_value = plugin_b
        definition_c.return_value = plugin_c
        
        plugin_source = dict(zip(args.names, definitions))

        def side_effect(name):
            return plugin_source[name]
        
        self.quartermaster.get_plugin.side_effect = side_effect
        self.strategy.function(args)
        self.assertEqual(self.quartermaster, self.strategy.quartermaster)
        self.assertEqual(self.quartermaster.external_modules, args.modules)
        for definition in definitions:
            definition.return_value.fetch_config.assert_called_with()

        args.names.append('d')
        definition_d = MagicMock()
        definition_d.side_effect = TypeError("unknown plugin")
        plugin_source['d'] = definition_d

        # nothing should happen, because it handles unknown plugins
        self.strategy.function(args)

        # and the decorator handles other errors
        definition_a.side_effect = AttributeError("plugin implementation error")
        self.strategy.function(args)
        return
