import os

try:
    from setuptools import setup, find_packages # Always prefer setuptools over distutils
except ImportError:
    from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))
# Get the long description from the relevant file
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='mrrapi',
    version='0.3.4',
    url='https://github.com/jcwoltz/mrrapi',
    description='MinigRigRentals.com python API integration',
    long_description=read('README.rst') + '\n\n' + read('CHANGES.txt'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Office/Business :: Financial"
    ],
    author='jcwoltz',
    author_email='jwoltz@gmail.com',
    keywords='mrr miningrigrentals api bitcoin',
    packages=find_packages(exclude=['contrib', 'example*', 'docs', 'tests*']),
    install_requires=['requests'],
    test_suite="mrrapi",
    entry_points={
        'console_scripts': [
            'listmyrigs = tools.list_myrigs:main',
            'updaterigprice = tools.updaterigprice:main'
        ]
    }
)
