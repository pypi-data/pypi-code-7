# -*- coding:utf-8 -*-
import sys
sys.path.insert(0,'/usr/lib/pyshared/python2.7')

from setuptools import setup, find_packages

import airtest

long_description = ''
try:
    with open('README') as f:
        long_description = f.read()
except:
    pass

setup(
      name='airtest_for_h9',
      version=airtest.__version__,
      description='mobile test(black air) python lib',
      long_description=long_description,

      author='zheng wen',
      author_email='wenzheng@whu.edu.cn',

      packages = find_packages(),
      include_package_data=True,
      package_data={},
      install_requires=[
          #'androidviewclient >= 7.1.1',
          'Appium-Python-Client >= 0.10',
          'click >= 3.3',
          'fuckit >= 4.8.0',
          'humanize >= 0.5',
          'pystache >= 0.5.4',
          # 'requests >= 2.4.3',
          'Flask >= 0.10.1',
          # 'pony >= 0.5.3',
          ],
      entry_points='''
      [console_scripts]
      air.test = airtest.cli2:main
      ''')