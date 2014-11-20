#!/usr/bin/env python

import os

from setuptools import setup

version = '0.2.0'
name = 'rubygemsrecipe'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name=name,
      version=version,
      description="zc.buildout recipe for installing ruby gems.",
      long_description=(read('README.rst') + '\n' + read('CHANGES.rst')),
      author='Mantas Zimnickas',
      author_email='sirexas@gmail.com',
      url='https://bitbucket.org/sirex/rubygemsrecipe',
      license='GPL',
      py_modules=['rubygems'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'six',
          'zc.buildout',
          'setuptools',
          'hexagonit.recipe.download'
      ],
      tests_require=[
          'mock',
          'pathlib',
      ],
      entry_points={
          'zc.buildout': ['default = rubygems:Recipe']
      },
      classifiers=[
          'Framework :: Buildout',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Topic :: Software Development :: Libraries :: Ruby Modules',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ])
