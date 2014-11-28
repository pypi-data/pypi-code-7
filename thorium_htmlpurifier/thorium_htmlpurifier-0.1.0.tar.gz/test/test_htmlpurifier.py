# -*- coding: utf-8 -*-

import unittest

from unittest.mock import MagicMock

from purifier.purifier import InvalidTagException, InvalidAttributeException

from thorium_htmlpurifier import HTMLValidator


class TestHTMLPurifierValidator(unittest.TestCase):
    def test_bad_tag(self):
        field = MagicMock()
        field.flags.__getitem__.return_value = 0
        value = "<script></script>"
        validator = HTMLValidator(field)
        self.assertRaises(InvalidTagException,
                          lambda: validator.validate(value))

    def test_bad_attribute(self):
        field = MagicMock()
        field.flags.__getitem__.return_value = 0
        value = "<div onclick='alert();'></div>"
        validator = HTMLValidator(field)
        self.assertRaises(InvalidAttributeException,
                          lambda: validator.validate(value))

    def test_valid_markup(self):
        field = MagicMock()
        field.flags.__getitem__.return_value = 0
        value = "<div></div><p></p><a></a><hr><br>"
        validator = HTMLValidator(field)
        self.assertTrue(validator.validate(value))
