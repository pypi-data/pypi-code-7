# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.

"""
Metaconfig tests.

Requires nose.

"""

import os

from unittest import TestCase
import tempfile
from cStringIO import StringIO

import ConfigParser

from metaconfig import MetaConfig, Error

def _make_test_config(**kwargs):
    conf = ConfigParser.RawConfigParser()

    conf.add_section('foo')
    conf.set('foo', 'a', '42')
    conf.set('foo', 'b', 'line 1\nline 2')

    conf.add_section('bar')
    for k, v in kwargs.items():
        conf.set('bar', k, v)

    return conf

_metaconfig_pat = """

[metaconfig]
configs = p1 p1.p2

[p1:foo]
a = 42
b = line 1
    line 2

[p1:bar]
%s

[p1.p2:foo]
a = 12
b = no
c = yes

"""

def _make_metaconfig(**kwargs):
    args = '\n'.join('%s = %s' % (k, kwargs[k]) for k in kwargs)
    text = _metaconfig_pat % args
    fh = StringIO(text)

    mf = ConfigParser.ConfigParser()
    mf.readfp(fh)

    return mf


class Test1(TestCase):
    def setUp(self):
        self.mf = MetaConfig()
        self.mf.add_config('p1', _make_test_config(x='1'))
        self.mf.add_config('p1.p2', _make_test_config(x='2'))

    def test_1(self):
        conf = self.mf.get_config('p1')
    
        assert conf.get('foo', 'a') == '42'

    def test_2(self):
        conf = self.mf.get_config('x')
        assert conf.sections() == []

    def test_3(self):
        conf = self.mf.get_config('p1.p2')

        assert conf.get('bar', 'x') == '2'

    def test_4(self):
        # Request non-existent conf with existing parent.
        conf = self.mf.get_config('p1.p3')

        assert conf.get('bar', 'x') == '1'

class Test2(TestCase):
    def setUp(self):
        self.mf = MetaConfig()

        fd, self.config_file = tempfile.mkstemp()
        fh = os.fdopen(fd, 'w')
        conf = _make_test_config(x='1')
        conf.write(fh)
        fh.close()

        
    def tearDown(self):
        os.remove(self.config_file)
        
    def test_1(self):
        self.mf.add_config_fh('p1', open(self.config_file))

        conf = self.mf.get_config('p1')
    
        assert conf.get('foo', 'a') == '42'
        assert conf.get('bar', 'x') == '1'

    def test_2(self):
        self.mf.add_config_file('p1', self.config_file)

        conf = self.mf.get_config('p1')
    
        assert conf.get('foo', 'a') == '42'
        assert conf.get('bar', 'x') == '1'

class Test3(TestCase):
    def setUp(self):
        self.mf = MetaConfig.from_config(_make_metaconfig(x='1'))

    def test_1(self):
        conf = self.mf.get_config('p1')
        
        assert conf.get('foo', 'a') == '42'
        assert conf.get('bar', 'x') == '1'
