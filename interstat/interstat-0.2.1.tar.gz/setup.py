#!/usr/bin/env python
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test


class Tox(test):
    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


setup(
    name='interstat',
    description='An HTML formatter for IRC log files',
    version='0.2.1',
    author='Kevin Xiwei Zheng',
    author_email='blankplacement+interstat@gmail.com',
    url='https://github.com/kxz/interstat',
    license='X11',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Communications :: Chat :: Internet Relay Chat',
        'Topic :: Text Processing :: Markup :: HTML'],
    keywords='irc html log',
    packages=find_packages(),
    package_data={
        'interstat': [
            'templates/*.css',
            'templates/*.html',
            'templates/message/*.html']},
    entry_points={
        'console_scripts': ['interstat=interstat.__main__:main']},
    install_requires=[
        'future',
        'Jinja2'],
    tests_require=[
        'tox'],
    cmdclass={
        'test': Tox})
