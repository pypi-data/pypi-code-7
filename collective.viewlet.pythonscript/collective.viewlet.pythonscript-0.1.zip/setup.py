from setuptools import setup, find_packages
import os

version = '0.1'

long_description = (
    open('README.md').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name='collective.viewlet.pythonscript',
      version=version,
      description="Viewlet rendering collection of items returned by customizable Python scripts",
      long_description=long_description,
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
          "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      keywords='',
      author='Radoslaw Jankiewicz',
      author_email='radoslaw.jankiewicz@stxnext.pl',
      url='https://github.com/collective/collective.viewlet.pythonscript',
      license='GPLv2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['collective', 'collective.viewlet'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'Products.CMFCore',
          'Products.CMFPlone>=4.1',
          'Products.GenericSetup',
          'Products.statusmessages',
          'archetypes.schemaextender',
          'collective.portlet.pythonscript',
          'setuptools',
          'zope.interface',
          'zope.schema',
      ],
      extras_require={
          'test': [
              'plone.app.testing',
              'unittest2',
              'zope.component',
          ],
      },
      entry_points="""
# -*- Entry points: -*-
[z3c.autoinclude.plugin]
target = plone
""",
      )
