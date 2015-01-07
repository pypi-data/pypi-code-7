#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from distutils.core import setup
from distutils.extension import Extension
import struct

_PY_BIT = struct.calcsize('P') * 8

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

package_data = {
    'kontocheck': ['data/blz.lut2', 'data/scl.db'],
    }
        
if os.name == 'nt':
    package_data['kontocheck'].append('lib/kontocheck%s.dll' % _PY_BIT)
    ext_modules = None
else:
    ext_modules = [
        Extension('kontocheck.lib.kontocheck',
            sources=['lib/konto_check/konto_check.c'],
            libraries=['z'],
        ),
    ]

dist = setup(
    name='kontocheck',
    version='5.5.6',
    author='Thimo Kraemer',
    author_email='thimo.kraemer@joonis.de',
    url='http://www.joonis.de/de/software/sepa-ebics-client/kontocheck',
    description='Python ctypes wrapper of the konto_check library.',
    long_description=read('README.rst'),
    keywords=('kontocheck', 'iban'),
    download_url='',
    license='LGPLv3',
    ext_modules=ext_modules,
    package_dir={'kontocheck': 'src'},
    packages=['kontocheck'],
    package_data=package_data,
    )
