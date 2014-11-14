from setuptools import setup, find_packages
import os

version = '0.0.6'

setup(name='collective.slickslideshow',
      version=version,
      description="Slick Slideshow solution for Plone.",
      long_description=open("README.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='slideshow',
      author='Andre Goncalves',
      author_email='andre@intk.com',
      url='https://github.com/intk/collective.slickslideshow',
      download_url='https://github.com/intk/collective.slickslideshow/tarball/0.0.1',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
      ],
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
