import os
import sys

from setuptools import setup, find_packages

sys.path.insert(0, os.path.abspath('lib'))
from htdataredirector import __version__

setup(
    name='htdataredirector',
    version=__version__,
    packages=find_packages('lib'),
    package_dir={
        '': 'lib'
    },
    entry_points={
        'console_scripts': [
            'htdataclient = htdataredirector.client:runner',
        ],
    },
    install_requires=[
        'pyserial >= 2.6.7',
        'httplib2 >= 0.7'
    ],
    package_data={
    '': ['*.txt', '*.rst', '*.md']
    },
    description='',
    author='Johnny Robeson',
    author_email='johnny@localmomentum.net',
    url='https://github.com/lazerball/htdataredirector',
    license='AGPLv3+',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    use_2to3=False,
)
