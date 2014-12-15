#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_exreporter
----------------------------------

Tests for `exreporter` module.
"""

import unittest
from mock import patch, MagicMock
from exreporter import exreporter
from exreporter.stores import Stores


class TestExreporter(unittest.TestCase):

    @patch('exreporter.exreporter.Reporter')
    def test_report_issue_with_defaults(self, Reporter):
        Reporter.return_value = reporter = MagicMock()
        credentials = object()
        store_name = 'some_store'

        exreporter.report_issue(credentials=credentials, store_name=store_name)

        reporter.report.assert_called_once_with(
            max_comments=50, include_locals=True, labels=['Bug'], time_delta=10)

    @patch('exreporter.exreporter.report_issue')
    def test_report_github_issue_with_defaults(self, report_issue):
        credentials = object()

        exreporter.report_github_issue(credentials=credentials)

        report_issue.assert_called_once_with(
            credentials=credentials, store_name='github')

if __name__ == '__main__':
    unittest.main()
