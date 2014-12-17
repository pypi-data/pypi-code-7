from setuptools import setup
import sys
setup(
    name='paymill-jsonobject',
    version='0.7.1beta',
    author='Aleksandar Yalnazov',
    author_email='aleksandar.yalnazov@paymill.de',
    description='This is a fork of jsonobject library and is only intended to be used temporary until jsonobject 0.7.0 release is out.',
    long_description='This is a fork of jsonobject library and is only intended to be used temporary until jsonobject 0.7.0 release is out.',
    url='https://github.com/dannyroberts/jsonobject',
    packages=['jsonobject'],
    install_requires=['six'],
    tests_require=['unittest2'] if sys.version_info[0] == 2 else [],
    test_suite='test',
)
