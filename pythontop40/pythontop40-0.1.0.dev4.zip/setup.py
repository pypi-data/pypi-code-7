from setuptools import find_packages, setup
import json
from os import path

PACKAGE_DIR = "pythontop40"
LONG_DESCRIPTION_FILE = "README.rst"
PROJECT_DIR = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(PROJECT_DIR, LONG_DESCRIPTION_FILE), encoding='utf-8') as f:
    long_description = f.read()

with open(
        '{}/package_info.json'.format(PACKAGE_DIR)
) as fp:
    _info = json.load(fp)

setup(
    name=_info['name'],
    version=_info['version'],
    packages=find_packages(exclude=['tests']),
    url=_info['url'],
    license=_info['license'],
    author=_info['author'],
    author_email=_info['author_email'],
    description=_info['description'],
    long_description=long_description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=[
        'munch==2.0.2',
        'nap==2.0.0',
        'arrow==0.4.4',
        'booby>=0.7.0'
    ],
    dependency_links=[
      'https://github.com/DannyGoodall/booby.git#egg=booby'
    ]
)
