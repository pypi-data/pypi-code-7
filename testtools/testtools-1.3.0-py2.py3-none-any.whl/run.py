# Copyright (c) 2009 testtools developers. See LICENSE for details.

"""python -m testtools.run testspec [testspec...]

Run some tests with the testtools extended API.

For instance, to run the testtools test suite.
 $ python -m testtools.run testtools.tests.test_suite
"""

import argparse
from functools import partial
import os.path
import unittest2 as unittest
import sys

from extras import safe_hasattr

from testtools import TextTestResult, testcase
from testtools.compat import classtypes, istext, unicode_output_stream
from testtools.testsuite import filter_by_ids, iterate_tests, sorted_tests


defaultTestLoader = unittest.defaultTestLoader
defaultTestLoaderCls = unittest.TestLoader
have_discover = True
discover_impl = unittest.loader

# Kept for API compatibility, but no longer used.
BUFFEROUTPUT = ""
CATCHBREAK = ""
FAILFAST = ""
USAGE_AS_MAIN = ""

def list_test(test):
    """Return the test ids that would be run if test() was run.

    When things fail to import they can be represented as well, though
    we use an ugly hack (see http://bugs.python.org/issue19746 for details)
    to determine that. The difference matters because if a user is
    filtering tests to run on the returned ids, a failed import can reduce
    the visible tests but it can be impossible to tell that the selected
    test would have been one of the imported ones.

    :return: A tuple of test ids that would run and error strings
        describing things that failed to import.
    """
    unittest_import_strs = set([
        'unittest2.loader.ModuleImportFailure.',
        'unittest.loader.ModuleImportFailure.',
        'discover.ModuleImportFailure.'
        ])
    test_ids = []
    errors = []
    for test in iterate_tests(test):
        # Much ugly.
        for prefix in unittest_import_strs:
            if test.id().startswith(prefix):
                errors.append(test.id()[len(prefix):])
                break
        else:
            test_ids.append(test.id())
    return test_ids, errors


class TestToolsTestRunner(object):
    """ A thunk object to support unittest.TestProgram."""

    def __init__(self, verbosity=None, failfast=None, buffer=None,
        stdout=None):
        """Create a TestToolsTestRunner.

        :param verbosity: Ignored.
        :param failfast: Stop running tests at the first failure.
        :param buffer: Ignored.
        :param stdout: Stream to use for stdout.
        """
        self.failfast = failfast
        if stdout is None:
            stdout = sys.stdout
        self.stdout = stdout

    def list(self, test):
        """List the tests that would be run if test() was run."""
        test_ids, errors = list_test(test)
        for test_id in test_ids:
            self.stdout.write('%s\n' % test_id)
        if errors:
            self.stdout.write('Failed to import\n')
            for test_id in errors:
                self.stdout.write('%s\n' % test_id)
            sys.exit(2)

    def run(self, test):
        "Run the given test case or test suite."
        result = TextTestResult(
            unicode_output_stream(self.stdout), failfast=self.failfast)
        result.startTestRun()
        try:
            return test.run(result)
        finally:
            result.stopTestRun()


####################
# Taken from python 2.7 and slightly modified for compatibility with
# older versions. Delete when 2.7 is the oldest supported version.
# Modifications:
#  - If --catch is given, check that installHandler is available, as
#    it won't be on old python versions or python builds without signals.
#  - --list has been added which can list tests (should be upstreamed).
#  - --load-list has been added which can reduce the tests used (should be
#    upstreamed).


class TestProgram(unittest.TestProgram):
    """A command-line program that runs a set of tests; this is primarily
       for making test modules conveniently executable.
    """

    # defaults for testing
    module=None
    verbosity = 1
    failfast = catchbreak = buffer = progName = None
    _discovery_parser = None

    def __init__(self, module=__name__, defaultTest=None, argv=None,
                    testRunner=None, testLoader=defaultTestLoader,
                    exit=True, verbosity=1, failfast=None, catchbreak=None,
                    buffer=None, stdout=None):
        if module == __name__:
            self.module = None
        elif istext(module):
            self.module = __import__(module)
            for part in module.split('.')[1:]:
                self.module = getattr(self.module, part)
        else:
            self.module = module
        if argv is None:
            argv = sys.argv
        if stdout is None:
            stdout = sys.stdout
        self.stdout = stdout

        self.exit = exit
        self.failfast = failfast
        self.catchbreak = catchbreak
        self.verbosity = verbosity
        self.buffer = buffer
        self.defaultTest = defaultTest
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        self.listtests = False
        self.load_list = None
        self.testRunner = testRunner
        self.testLoader = testLoader
        progName = argv[0]
        if progName.endswith('%srun.py' % os.path.sep):
            elements = progName.split(os.path.sep)
            progName = '%s.run' % elements[-2]
        else:
            progName = os.path.basename(argv[0])
        self.progName = progName
        self.parseArgs(argv)
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        if self.load_list:
            # TODO: preserve existing suites (like testresources does in
            # OptimisingTestSuite.add, but with a standard protocol).
            # This is needed because the load_tests hook allows arbitrary
            # suites, even if that is rarely used.
            source = open(self.load_list, 'rb')
            try:
                lines = source.readlines()
            finally:
                source.close()
            test_ids = set(line.strip().decode('utf-8') for line in lines)
            self.test = filter_by_ids(self.test, test_ids)
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        if not self.listtests:
            self.runTests()
        else:
            runner = self._get_runner()
            if safe_hasattr(runner, 'list'):
                runner.list(self.test)
            else:
                for test in iterate_tests(self.test):
                    self.stdout.write('%s\n' % test.id())

    def _getParentArgParser(self):
        parser = super(TestProgram, self)._getParentArgParser()
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        parser.add_argument('-l', '--list', dest='listtests', default=False,
            action='store_true', help='List tests rather than executing them')
        parser.add_argument('--load-list', dest='load_list', default=None,
            help='Specifies a file containing test ids, only tests matching '
                'those ids are executed')
        return parser

    def _do_discovery(self, argv, Loader=None):
        super(TestProgram, self)._do_discovery(argv, Loader=Loader)
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        self.test = sorted_tests(self.test)

    def runTests(self):
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        if (self.catchbreak
            and getattr(unittest, 'installHandler', None) is not None):
            unittest.installHandler()
        testRunner = self._get_runner()
        self.result = testRunner.run(self.test)
        if self.exit:
            sys.exit(not self.result.wasSuccessful())

    def _get_runner(self):
        # XXX: Local edit (see http://bugs.python.org/issue22860)
        if self.testRunner is None:
            self.testRunner = TestToolsTestRunner
        try:
            testRunner = self.testRunner(verbosity=self.verbosity,
                                         failfast=self.failfast,
                                         buffer=self.buffer,
                                         stdout=self.stdout)
        except TypeError:
            # didn't accept the verbosity, buffer, failfast or stdout arguments
            # Try with the prior contract
            try:
                testRunner = self.testRunner(verbosity=self.verbosity,
                                             failfast=self.failfast,
                                             buffer=self.buffer)
            except TypeError:
                # Now try calling it with defaults
                try:
                    testRunner = self.testRunner()
                except TypeError:
                    # it is assumed to be a TestRunner instance
                    testRunner = self.testRunner
        return testRunner



################

def main(argv, stdout):
    program = TestProgram(argv=argv, testRunner=partial(TestToolsTestRunner, stdout=stdout),
        stdout=stdout)

if __name__ == '__main__':
    main(sys.argv, sys.stdout)
