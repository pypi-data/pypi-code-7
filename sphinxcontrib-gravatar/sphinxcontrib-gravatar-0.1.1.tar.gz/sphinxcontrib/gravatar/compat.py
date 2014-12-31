# -*- coding: utf-8 -*-
"""
    sphinxcontrib.gravatar.compat
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :author: tell-k <ffk2005@gmail.com>
    :copyright: tell-k. All Rights Reserved.
"""
from __future__ import (
    division,
    print_function,
    absolute_import,
    unicode_literals,
)

try:
    from urllib import urlopen  # NOQA
except:
    from urllib.request import urlopen  # NOQA

try:
    from urllib import urlencode  # NOQA
except:
    from urllib.parse import urlencode  # NOQA
