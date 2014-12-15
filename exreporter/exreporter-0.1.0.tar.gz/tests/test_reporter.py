# -*- coding: utf-8 -*-

"""
test_reporter
----------------------------------

Tests for `exreporter.reporter` module.
"""

import unittest
from mock import patch, MagicMock

from exreporter.reporter import Reporter


class TestReporter(unittest.TestCase):

    @patch('exreporter.reporter.Formats')
    @patch('exreporter.reporter.StackTrace')
    @patch('exreporter.reporter.Stores')
    def test_reporter_report_with_defaults(self, Stores, StackTrace, Formats):
        Stores.some_name = store_cls = MagicMock()
        store = store_cls()
        store_name = 'some_name'
        credentials = object()
        stack_trace = StackTrace()
        stack_trace.exception = ValueError

        reporter = Reporter(credentials=credentials, store_name=store_name)

        reporter.report()

        store.create_or_update_issue.assert_called_once_with(
            title=Formats.title.format(),
            culprit=Formats.culprit.format(),
            body='''{}

{}
'''.format(Formats.body.format(), Formats.culprit.format()))
