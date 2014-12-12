import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    'Hook into py.test to run the test suite'
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def readme():
    'Dump out the readme'
    with open('README.rst') as f:
        return f.read()

setup(
    name='bade',
    version='0.0.3',
    description='Micro-blogging with rST',
    packages=[
        'bade',
        'bade.utils',
    ],
    long_description=readme(),
    url='http://bmcorser.github.com/bade',
    author='bmcorser',
    author_email='bmcorser@gmail.com',
    install_requires=[
        'click',
        'docutils',
        'mako',
        'sass-cli',
        'pyyaml',
    ],
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    entry_points='''
        [console_scripts]
        bade=bade.cli:main
    '''
)
