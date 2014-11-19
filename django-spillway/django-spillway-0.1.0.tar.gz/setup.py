#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='django-spillway',
      version='0.1.0',
      description='Geodata extensions for Django REST Framework',
      long_description=open('README.rst').read(),
      author='Brian Galey',
      author_email='bkgaley@gmail.com',
      url='https://github.com/bkg/django-spillway',
      packages=find_packages(exclude=['tests*']),
      include_package_data=True,
      # FIXME: setup.py test installs eggs from PyPI and does not appear to use
      # the virtualenv versions, causes problems w/ symlinks to greenwich
      #install_requires=['django', 'djangorestframework', 'greenwich'],
      # FIXME: This is a *MAJORFRACKINGPROBLEM* since greenwich 0.2 is
      # installed which doesn't have envelope.polygon, breaks rstore creation
      # validation! The easiest fix may be to avoid running "setup.py test" and
      # just "./runtests.py" instead.
      install_requires=['django', 'djangorestframework'],
      extras_requires={'mapnik': ['Mapnik>=2.0']},
      #entry_points={'spillway': ['spillway.mapnik = spillway.mapnik[mapnik]']},
      #entry_points={'spillway': ['compat = compat[mapnik]']},
      license='BSD',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
      ],
      test_suite='runtests.runtests')
