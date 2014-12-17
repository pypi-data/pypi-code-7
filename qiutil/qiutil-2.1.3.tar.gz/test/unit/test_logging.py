import os
import shutil
from nose.tools import (assert_equal, assert_true)
from qiutil import logging
from qiutil.logging import logger

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
"""The test parent directory."""

FIXTURE = os.path.join(ROOT, 'fixtures', 'logging', 'logging.yaml')
"""The test fixture logging configuration file."""

RESULTS = os.path.join(ROOT, 'results', 'fixtures', 'logging')
"""The test result parent directory."""

RESULT = os.path.join(RESULTS, 'log', 'qiutil.log')
"""The resulting test log."""


class TestLoggingHelper(object):

    """The logging unit tests."""

    def setUp(self):
        shutil.rmtree(RESULTS, True)

    def tearDown(self):
        shutil.rmtree(RESULTS, True)

    def test_filename(self):
        logging.configure('test', filename=RESULT)
        logger('test').info("Test info log message.")
        logger('test').debug("Test debug log message.")
        assert_true(os.path.exists(RESULT),
                    "The log file was not created: %s" % RESULT)
        with open(RESULT) as fs:
            msgs = fs.readlines()
        assert_true(not not msgs, "No log messages in %s" % RESULT)
        assert_equal(len(msgs), 1, "Extraneous log messages in %s" % RESULT)

    def test_level(self):
        logging.configure('test', filename=RESULT, level='DEBUG')
        logger('test').info("Test info log message.")
        logger('test').debug("Test debug log message.")
        assert_true(os.path.exists(RESULT),
                    "The log file was not created: %s" % RESULT)
        with open(RESULT) as fs:
            msgs = fs.readlines()
        assert_true(not not msgs, "No log messages in %s" % RESULT)
        assert_equal(len(msgs), 2, "Extraneous log messages in %s" % RESULT)

if __name__ == "__main__":
    import nose

    nose.main(defaultTest=__name__)
