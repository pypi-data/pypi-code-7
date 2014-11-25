from setuptools import setup, find_packages
import os

version = '1.0b2'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

setup(name=u'ngi.notify.datadog',
      version=version,
      description="Notify the Plone operation event to the DataDog",
      long_description=long_description,
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Takashi NAGAI',
      author_email='ngi644@gmail.com',
      url='https://github.com/ngi644/ngi.notify.datadog',
      license='gpl',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['ngi', 'ngi.notify'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'plone.app.registry',
          'plone.api',
          'dogapi',
          'dogstatsd-python',
          'zope.processlifetime',
      ],
      extras_require={'test': ['plone.app.testing']},
      entry_points="""
      # -*- Entry points: -*-
  	  [z3c.autoinclude.plugin]
  	  target = plone
      """,
      )
