from setuptools import setup, find_packages
import os

version = '0.1.0'

setup(name='django_drole',
      version=version,
      description="Django Drole: Zope/Plone inspired roles/permissions",
      long_description=open("README.md").read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Ivo van der Wijk',
      author_email='two@in.m3r.nl',
      url='http://github.com/iivvoo/django_drole',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=[],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'pytest',
          'coverage',
      ],
      entry_points={
      },

      )

