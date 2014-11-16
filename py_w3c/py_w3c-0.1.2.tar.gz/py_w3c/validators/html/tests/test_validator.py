#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unittest
from StringIO import StringIO

from py_w3c.validators.html.validator import HTMLValidator
from py_w3c.exceptions import ValidationFault


TESTS_DIR = os.path.dirname(__file__)


class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = HTMLValidator(charset='utf-8')

    def _fullpath(self, filename):
        '''
        returns full for file in tests directory.
        '''
        return os.path.join(TESTS_DIR, filename)

    def test_url_validation(self):
        # I know exactly there is no errors on datetostr.org
        self.validator.validate('http://datetostr.org')
        self.assertEqual(self.validator.errors, [])
        self.assertEqual(self.validator.warnings, [])

    def test_file_validation(self):
        with open(self._fullpath('file.html')) as f:
            self.validator.validate_file(f)
            self.assertEqual(len(self.validator.errors), 1)
            self.assertEqual(int(self.validator.errors[0].get('line')), 3)

    def test_validation_by_file_name(self):
        with open(self._fullpath('file.html')) as f:
            self.validator.validate_file(f.name)
            self.assertEqual(len(self.validator.errors), 1)
            self.assertEqual(int(self.validator.errors[0].get('line')), 3)

    def test_validation_by_file_with_unicode_name(self):
        with open(self._fullpath(u'мой-файл.html')) as f:
            self.validator.validate_file(f.name)
            self.assertEqual(len(self.validator.errors), 1)
            self.assertEqual(int(self.validator.errors[0].get('line')), 3)

    def test_in_memory_file_validation(self):
        HTML = '''<!DOCTYPE html>
            <html>
            <head bad-attr="i'm bad">
                <title>py_w3c test</title>
            </head>
                <body>
                    <h1>Hello py_w3c</h1>
                </body>
            </html>
        '''
        self.validator.validate_file(StringIO(HTML))
        self.assertEqual(len(self.validator.errors), 1)
        self.assertEqual(int(self.validator.errors[0].get('line')), 3)

    def test_fragment_validation(self):
        fragment = u'''<!DOCTYPE html>
            <html>
                <head>
                    <title>testing py_w3c</title>
                </head>
                <body>
                    <badtag>i'm bad</badtag>
                    <div>my div</div>
                </body>
            </html>
        '''.encode('utf-8')
        self.validator.validate_fragment(fragment)
        self.assertEqual(len(self.validator.errors), 1)
        self.assertEqual(int(self.validator.errors[0].get('line'),), 7)

    def test_passing_doctype_forces_validator_to_use_given_doctype(self):
        doctype = 'XHTML 1.0 Strict'
        val = HTMLValidator(doctype=doctype)
        # I know exactly there is no errors on datetostr.org
        val.validate('http://datetostr.org')
        self.assertTrue(doctype in val.result.doctype)

    def test_passing_charset_forces_validator_to_use_given_charset(self):
        val = HTMLValidator(charset='windows-1251')
        val.validate('http://datetostr.org')
        self.assertEqual(val.result.charset, 'windows-1251')

    def test_passing_wrong_charset_raises_ValidationFault_exception(self):
        val = HTMLValidator(charset='win-1251')
        self.assertRaises(ValidationFault, val.validate, 'http://datetostr.org')
