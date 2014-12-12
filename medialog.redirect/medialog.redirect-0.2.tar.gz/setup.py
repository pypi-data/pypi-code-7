# -*- coding: utf-8 -*-
"""
This module contains  medialog.redirect
"""
import os
from setuptools import setup, find_packages


version = '0.2'


setup(name='medialog.redirect',
      version=version,
      description="A redirecting browser view",
      long_description='A view that takes two variables, index and index_value and redirects to the first content item that is found',
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        ],
      keywords='redirect plone diazo',
      author='Espen Moe-Nilssen',
      author_email='espen at medialog no',
      url='http://github.com/espenmn/medialog.redirect',
      license='gpl',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['medialog'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['plone.api',
      				'setuptools',
      				],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
