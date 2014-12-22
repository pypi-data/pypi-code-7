
# python standard library
import unittest
import random
import argparse

# third-party
try:
    from mock import MagicMock, patch
except ImportError:
    pass


#third-party
import docopt

# this package
from  ape.interface.arguments.arguments import BaseArguments
from ape.interface.ubootkommandant import UbootKommandant
from ape import BaseClass
from ape import VERSION
import ape.interface.arguments.arguments

usage = ape.interface.arguments.arguments.__doc__

class TestBaseArguments(unittest.TestCase):
    def setUp(self):
        self.args = ['cow']
        self.arguments = BaseArguments(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        arguments = BaseArguments()
        self.assertIsInstance(arguments, BaseClass)
        self.assertEqual(arguments.usage, usage)
        self.assertIsNone(arguments.args)
        return

    def test_debug(self):
        """
        Does it correctly set the debug value?
        """
        self.assertFalse(self.arguments.debug)
        self.arguments.reset()

        self.arguments.args = '--debug cow'.split()
        self.assertTrue(self.arguments.debug)

        # mutual exclusivity
        self.arguments.reset()
        self.arguments.args = '--debug --silent cow'.split()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.debug
        return

    def test_silent(self):
        """
        Does it set the silent option?
        """
        self.assertFalse(self.arguments.silent)

        self.arguments.reset()
        self.arguments.args = '--silent cow'.split()
        self.assertTrue(self.arguments.silent)

        # test mutual-exclusivity
        self.arguments.reset()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.args = '--silent --debug cow'.split()
            self.arguments.silent
        return

    def test_pudb(self):
        """
        Does it set the pudb option?
        """
        self.assertFalse(self.arguments.pudb)

        self.arguments.reset()
        self.arguments.args = '--pudb cow'.split()
        self.assertTrue(self.arguments.pudb)

        self.arguments.reset()
        self.arguments.args = "--pudb --pdb cow".split()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.pudb
        return

    def test_pdb(self):
        """
        Does it set the `pdb` option?
        """
        self.assertFalse(self.arguments.pdb)

        self.arguments.reset()
        self.arguments.args = '--pdb cow'.split()
        self.assertTrue(self.arguments.pdb)

        # mutually exclusive
        self.arguments.reset()
        self.arguments.args = '--pdb --pudb cow'.split()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.pdb           
        return

    def test_trace(self):
        """
        Does it set the trace flag?
        """
        self.assertFalse(self.arguments.trace)

        self.arguments.reset()
        self.arguments.args = '--trace  cow'.split()
        self.assertTrue(self.arguments.trace)

        self.arguments.reset()
        self.arguments.args = '--trace --callgraph cow'.split()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.trace
        return

    def test_callgraph(self):
        """
        Does it set the callgraph option?
        """
        self.assertFalse(self.arguments.callgraph)
        
        self.arguments.reset()
        self.arguments.args = "--callgraph cow".split()
        self.assertTrue(self.arguments.callgraph)

        self.arguments.reset()
        self.arguments.args = "--callgraph --trace cow".split()
        with self.assertRaises(docopt.DocoptExit):
            self.arguments.callgraph
        return

    def test_version(self):
        """
        Does it set the version?
        """
        mock_docopt = MagicMock()
        for option_first in (True, False):
            arguments = BaseArguments(options_first=option_first)    

            with patch('docopt.docopt', mock_docopt):
                arguments.debug
            mock_docopt.assert_called_with(doc=usage,
                                           argv=None,
                                           options_first=option_first,
                                           version=VERSION)
        
        
            mock_docopt.reset()
        return

    def test_options_first(self):
        """
        Is the default for options first True?
        """
        self.assertTrue(self.arguments.options_first)
        arguments = BaseArguments(options_first=False)
        self.assertFalse(arguments.options_first)
        return

    def test_subcommands(self):
        """
        Does the BaseArguments have a UbootKommandant for the child classes?
        """
        self.assertIsInstance(self.arguments.subcommands, UbootKommandant)
        return

    def test_command(self):
        """
        Does it set the command?
        """
        self.assertEqual('cow', self.arguments.command)
        command = random.choice('run fetch list check help'.split())
        
        self.arguments.reset()
        self.arguments.args = [command]
        self.assertEqual(command, self.arguments.command)
        return
# end class TestBaseArguments    
