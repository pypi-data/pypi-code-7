
# python standard library
import unittest
import random
import string

# third-party
from mock import MagicMock

# the ape
from ape.interface.arguments.helparguments import Help
from ape.interface.arguments.helparguments import HelpStrategy
from ape.interface.arguments.basestrategy import BaseStrategy


class TestHelp(unittest.TestCase):
    def setUp(self):
        self.args = ['help']
        self.arguments = Help(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build correctly?
        """
        arguments = Help(args=['help'])
        self.assertFalse(arguments.trace)
        return

    def test_width(self):
        """
        Does it get the screen-width?
        """
        self.assertEqual(self.arguments.width, 80)

        self.arguments.reset()
        width = random.randint(0, 100)
        self.arguments.args = self.args + ['--width', '{0}'.format(width)]
        self.assertEqual(width, self.arguments.width)
        return

    def test_modules(self):
        """
        Does it get a list of plugin modules?
        """
        # default is an empty list
        self.assertEqual([], self.arguments.modules)

        self.arguments.reset()
        modules = ["".join([random.choice(string.letters) for letter in xrange(random.randrange(1, 10))]) for
                   module in xrange(random.randrange(2, 10))]
        mod_options = "-m " + ' -m '.join(modules)
        self.arguments.args = self.args + mod_options.split()
        self.assertEqual(self.arguments.modules, modules)
        return

    def test_name(self):
        """
        Does it get the name of the plugin?
        """
        self.assertEqual('Ape', self.arguments.name)

        self.arguments.reset()
        name = ''.join([random.choice(string.letters) for letter in xrange(random.randrange(1, 10))])
        self.arguments.args = self.args + [name]
        self.assertEqual(name, self.arguments.name)
        return

    def test_whole_shebang(self):
        """
        Does it get modules, screen width and names?
        """
        width = random.randrange(2, 100)
        width_option = '-w {0}'.format(width)
        modules = ["".join([random.choice(string.letters) for letter in xrange(random.randrange(2, 10))]) for
                   module in xrange(random.randrange(2, 10))]
        mod_options = "-m " + ' -m '.join(modules)
        name = ''.join([random.choice(string.letters) for letter in xrange(random.randrange(2, 10))])

        self.arguments.args = self.args + [width_option] + mod_options.split() + [name]
        self.assertEqual(width, self.arguments.width)
        self.assertEqual(modules, self.arguments.modules)
        self.assertEqual(name, self.arguments.name)
        return


class TestHelpStrategy(unittest.TestCase):
    def test_constructor(self):
        """
        Does it build?
        """
        strategy = HelpStrategy()
        self.assertIsInstance(strategy, BaseStrategy)
        return

    def test_function(self):
        """
        Does it implement the `help` strategy?
        """
        args = MagicMock()
        quartermaster = MagicMock()
        HelpStrategy.quartermaster = quartermaster

        args.modules = 'x y z'.split()
        args.name = 'bob'
        args.width = 38 
        definition_bob = MagicMock()

        plugin_bob = MagicMock()

        definition_bob.return_value = plugin_bob
        plugin_definitions = {'bob': definition_bob}
        def side_effect(name):
            return plugin_definitions[name]
        
        quartermaster.get_plugin.side_effect = side_effect
        
        strategy = HelpStrategy()
        strategy.function(args)

        self.assertEqual(quartermaster.external_modules, args.modules)
        quartermaster.get_plugin.assert_called_with('bob')
        plugin_bob.help.assert_called_with(args.width)

        # type-errors are considered a user-mistake
        quartermaster.get_plugin.side_effect = TypeError("no comprende")
        strategy.function(args)
        quartermaster.list_plugins.assert_called_with()

        #get rid of the TypeError so we can test other errors
        quartermaster.get_plugin.side_effect = side_effect
        plugin_bob.help.side_effect = AttributeError("no such attribute")
        strategy.function(args)

        plugin_bob.help.side_effect = Exception("aaaaaaaaahhhhhhh")
        strategy.function(args)
        plugin_bob.help.assert_called_with(args.width)
        return
