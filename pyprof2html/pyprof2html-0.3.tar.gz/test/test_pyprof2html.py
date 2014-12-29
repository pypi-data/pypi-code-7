#!/usr/bin/env python
"""test_pyprof2html - testing script for pyprof2html
"""
import unittest

from pyprof2html._compat import PY2

if not PY2:
    from python2.tests import FileTypeCheckTestCase
    from python2.tests import ConvertUnitTestCase
    # TODO: not enough
    # from python2.tests import ExecuteHtmlTestCase
    # from python2.tests import ExecuteRawTestCase
    from python2.tests import ColorMappingTestCase
    from python2.tests import FindFileCodecTestCase
    from python2.tests import CreateStylefileTestCase
    # TODO: not enough
    # from python2.tests import CommandExeTestCase

    # TODO: not enough
    # from python3.tests import *
else:
    from python2.tests import *

unittest.main()

