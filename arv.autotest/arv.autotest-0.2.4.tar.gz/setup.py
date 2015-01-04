from setuptools import setup, find_packages
import sys, os

version = '0.2.4'

setup(name='arv.autotest',
      version=version,
      description="Run tests whenever a file changes",
      long_description=open("README.rst").read(),
      # https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
          "Natural Language :: English",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: 3.4",
          "Topic :: Software Development :: Testing",
      ],
      keywords='',
      author='Alexis Roda',
      author_email='alexis.roda.villalonga@gmail.com',
      url='https://github.com/patxoca/arv.autotest',
      license='GPLv3+',
      packages=find_packages(),
      namespace_packages=['arv'],
      include_package_data=True,
      package_data={
          "": ["images/*.png"]
      },
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
          "blessings",
          "pyinotify",
          "six",
      ],
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      autotest=arv.autotest.main:main
      """,
      )
