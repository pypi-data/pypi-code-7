#!/usr/bin/env python

from setuptools import setup

import re
import sys

# load our version from our init file
init_data = open('easy/__init__.py').read()
matches = re.search(r"__version__ = '([^']+)'", init_data, re.M)
if matches:
    version = matches.group(1)
else:
    raise RuntimeError("Unable to load version")

requirements = [
    'PyYAML==3.11',
    'Jinja2>=2.7,<2.8',
    'sh>=1.09'
]
if sys.version_info < (2, 7):
    requirements.append('argparse')

setup(
    name='easy',
    packages=['easy'],
    scripts=['scripts/easy'],
    include_package_data=True,
    version=version,
    license="Unlicense",
    description='A simple PaaS CLI which is inspired by Heroku.',
    author='StackStrap',
    author_email='info@stackstrap.org',
    url='https://github.com/stackstrap/easy',
    keywords=['paas', 'devops', 'vagrant', 'salt', 'docker'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=requirements
)
