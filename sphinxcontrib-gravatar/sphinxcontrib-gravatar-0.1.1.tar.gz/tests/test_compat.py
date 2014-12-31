# -*- coding: utf-8 -*-
"""
    unittest for sphinxcontrib.gravatar.compat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
    unicode_literals
)


class TestCompat(object):

    def test_import_urlopen(self):
        from sphinxcontrib.gravatar.compat import urlopen  # NOQA

    def test_import_urlencode(self):
        from sphinxcontrib.gravatar.compat import urlencode  # NOQA
