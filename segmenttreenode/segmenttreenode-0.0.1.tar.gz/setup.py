from setuptools import setup, find_packages
import os

setup(
    name = 'segmenttreenode',
    version = '0.0.1',
    keywords = ('segmenttree', 'segmenttreenode', 'segment', 'tree', 'node', 'egg'),
    description = 'Data structure for Segment Tree',
    license = 'MIT License',

    ong_description=open(os.path.join(os.path.dirname(__file__), 'README.txt')).read(),

    url = 'https://github.com/ramtee/segmenttreenode',
    author = 'Zhaonan Li',
    author_email = 'zhaonanproject@gmail.com',

    packages = find_packages(),
    package_data = {'': ['*.*']},
    include_package_data = True,
    platforms = 'any',
    install_requires = [],
)