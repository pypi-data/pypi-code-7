import sys

from .runner import TestRunner
from hatak.command import Command


class TosterCommand(Command):

        def __init__(self, fixtures):
            super().__init__('toster', 'tests')
            self.fixtures = fixtures

        def __call__(self, args):
            self.app.factory.run_module('tests')
            self.app.factory.run_module_without_errors('tests')
            sys.argv.pop(0)
            TestRunner(self.app, self.fixtures)()
