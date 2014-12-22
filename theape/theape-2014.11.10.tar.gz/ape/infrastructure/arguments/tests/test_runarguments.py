
# python standard library
import unittest

# third-party
from mock import MagicMock, patch

# the ape
from ape.interface.arguments.runarguments import Run
from ape.interface.arguments.arguments import BaseArguments
from ape.interface.arguments.runarguments import RunArgumentsConstants
from ape.interface.arguments.runarguments import RunStrategy
from ape.interface.arguments.basestrategy import BaseStrategy



class TestRunArguments(unittest.TestCase):
    def setUp(self):
        self.args = ['run']
        self.arguments = Run(args=self.args)
        return
    
    def test_constructor(self):
        """
        Does it build properly?
        """
        arguments = Run(args='run')
        self.assertIsInstance(arguments, BaseArguments)
        # test the inheritance
        self.assertFalse(arguments.debug)
        return

    def test_configfiles(self):
        """
        Does it get the configfiles list?
        """
        # test default
        self.assertEqual(self.arguments.configfiles,
                         RunArgumentsConstants.default_configfiles)

        #test arguments
        self.arguments.reset()
        configfiles =  'ape.ini cow.txt pie.bla'.split()
        self.arguments.args = self.args + configfiles
        self.assertEqual(self.arguments.configfiles, configfiles)
        return


class TestRunStrategy(unittest.TestCase):
    def setUp(self):
        self.build_ape = MagicMock()
        self.strategy = RunStrategy()
        self.args = MagicMock()
        self.args.trace = False
        self.args.callgraph = False
        self.ape = MagicMock()

        # monkey-patch
        self.strategy.build_ape = self.build_ape
        return
    
    def test_constructor(self):
        """
        Does it build?
        """
        strategy = RunStrategy()
        self.assertIsInstance(strategy, BaseStrategy)
        return

    def test_function(self):
        """
        Does it implement the strategy correctly?
        """
        configfiles = 'how now brown cow'.split()
        self.args.configfiles = configfiles
        # unsuccessful build
        self.build_ape.return_value = None
        self.strategy.function(self.args)
        self.build_ape.assert_called_with(configfiles)

        # succellful build
        self.build_ape.return_value = self.ape
        self.strategy.function(self.args)
        self.ape.assert_called_with()
        self.ape.close.assert_called_with()
        return

    def test_trace(self):
        """
        Does it trace the calls?
        """
        self.args.trace = True
        self.build_ape.return_value = self.ape

        # trace mocks the module import
        trace = MagicMock()
        # tracer mocks the Trace object
        tracer = MagicMock()
        trace.return_value = tracer
        with patch('trace.Trace', trace):
            self.strategy.function(self.args)
            print tracer.mock_calls
            tracer.runfunc.assert_called_with(self.ape)            
        return

    def test_errors(self):
        """
        Does it trap errors?
        """
        self.build_ape.return_value = self.ape
        self.ape.side_effect = RuntimeError("oop")
        self.strategy.function(self.args)
        return
