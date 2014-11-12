from setuptools import setup, find_packages
import os

version = '0.0.1'

setup(name='collective.leadmedia',
      version=version,
      description="Adds a slideshow to any dexterity folderish type.",
      long_description=open("README.txt").read() + "\n" +
                       open("docs/HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='Plone',
      author='Andre Goncalves',
      author_email='andre@intk.com',
      url='https://github.com/intk/collective.leadmedia',
      download_url='https://github.com/intk/collective.leadmedia/tarball/0.0.1',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'collective.folderishtypes==2.0b2',
          'collective.slickslideshow==0.0.6'
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
