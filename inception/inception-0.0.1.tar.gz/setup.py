# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from inception.version import APP


def read_description():
    with open('README.rst') as fd:
        return fd.read()


setup(name='inception',
      version=APP.version,
      description=APP.description,
      long_description=read_description(),
      classifiers=[
          'Development Status :: 1 - Planning',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
      ],
      keywords='templates,project creation,inception,project inception,start',
      author='Miguel Ángel García',
      author_email='miguelangel.garcia@gmail.com',
      url='https://github.com/magmax/inception',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'inquirer >= 2.1.2',
          'jinja2 >= 2.7.3',
      ],
      )
