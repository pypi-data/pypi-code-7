# -*- coding: utf-8 -*-

import sys

from setuptools.command.test import test as TestCommand
from setuptools import setup, find_packages
from inception.version import APP


def read_description():
    with open('README.rst') as fd:
        return fd.read()


class PyTest(TestCommand):
    user_options = [
        ('pytest-args=', 'a', "Arguments to pass to py.test"),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args or ['--cov-report=term-missing'])
        sys.exit(errno)


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
      cmdclass={'test': PyTest},
      tests_require=[
          'python-coveralls >= 2.4.2',
          'wheel',
          'pytest >= 2.6.1',
          'pytest-cov >= 1.7.0',
          'pytest-xdist >= 1.10',
          'pexpect',
      ],
      install_requires=[
          'inquirer >= 2.1.2',
          'jinja2 >= 2.7.3',
      ],
      )
