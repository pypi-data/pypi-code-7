
# python standard library
import unittest

# the ape
from ape.interface.arguments.argumentbuilder import ArgumentBuilder
from ape.interface.arguments.fetcharguments import Fetch
from ape.interface.arguments.runarguments import Run
from ape.interface.arguments.listarguments import List
from ape.interface.arguments.checkarguments import Check
from ape.interface.arguments.helparguments import Help


class TestArgumentBuilder(unittest.TestCase):
    def test_constructor(self):
        """
        Does it build?
        """
        builder = ArgumentBuilder(args=['fetch'])
        return

    def test_parse_args(self):
        """
        Does it work like argparse?
        """
        builder = ArgumentBuilder(args=['fetch'])
        args = builder()
        self.assertEqual(args.command, 'fetch')
        self.assertIsInstance(args, Fetch)

        builder.args = ['run']
        args = builder()
        self.assertIsInstance(args, Run)

        builder.args = ['list']
        args = builder()
        self.assertIsInstance(args, List)

        builder.args = ['check']
        args = builder()
        self.assertIsInstance(args, Check)

        builder.args = ['help']
        args = builder()
        self.assertIsInstance(args, Help)
        return
