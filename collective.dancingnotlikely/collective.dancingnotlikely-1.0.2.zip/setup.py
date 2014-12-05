from setuptools import setup, find_packages
import os

version = '1.0.2'

setup(name='collective.dancingnotlikely',
      version=version,
      description="A plugin for collective.dancing that add more elements to ignore-list in the composer",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='dancing newsletter composer filter',
      author='RedTurtle Technology',
      author_email='sviluppoplone@redturtle.it',
      url='https://plone.org/products/collective.dancingnotlikely',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.dancing',
      ],
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
