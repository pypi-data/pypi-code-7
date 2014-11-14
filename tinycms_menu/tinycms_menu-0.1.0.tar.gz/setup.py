from setuptools import setup, find_packages
import sys, os

version = '0.1.0'

setup(name='tinycms_menu',
      version=version,
      description="Menu addon for tinycms",
      classifiers=["Framework :: Django","License :: OSI Approved :: MIT License","Programming Language :: Python"], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='ccat',
      author_email='',
      url='https://www.whiteblack-cat.info/',
      license='MIT',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "tinycms",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
