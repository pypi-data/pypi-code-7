# BSD Licence
# Copyright (c) 2010, Science & Technology Facilities Council (STFC)
# All rights reserved.
#
# See the LICENSE file in the source distribution of this software for
# the full license text.


import tempfile
import os

from test_metaconfig import _make_metaconfig
from metaconfig import get_config, reset


def setup():
    global config_file

    fd, config_file = tempfile.mkstemp()
    mconf = _make_metaconfig(x='1')
    fh = os.fdopen(fd, 'w')
    mconf.write(fh)
    fh.close()

    os.environ['METACONFIG_CONF'] = config_file

def teardown():
    reset()
    os.remove(config_file)


def test_1():
    config = get_config('p1')
    assert config.get('foo', 'a') == '42'
