#!/usr/bin/env python
from setuptools import setup, find_packages
setup(name='django_linksets',
      description='A basic model to include administrable linksets\
      in templates.',
      version='2.0.3',
      url='https://github.com/gethee2anunnery/django-linksets',
      author="Sara Perry w/ Nina Pavlich",
      author_email='paraserry@gmail.com',
      packages=find_packages(exclude=['ez_setup']),
      zip_safe=False,
      include_package_data=True,
      install_requires=[
          'setuptools',
          'Django',
      ],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved',
          'Operating System :: OS Independent',
          'Programming Language :: Python'
      ]
      )
