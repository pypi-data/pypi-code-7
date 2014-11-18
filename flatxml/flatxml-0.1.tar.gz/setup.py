import os
import re

v = open(os.path.join(os.path.dirname(__file__), 'flatxml', '__init__.py'))
VERSION = re.compile(r".*__version__ = '(.*?)'", re.S).match(v.read()).group(1)
v.close()

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Transform XML blob, file, or OrderedDict to a flat CSV or dictionary.',
    'author': 'Carlos Eduardo Rivera',
    'url': 'URL to get it at.',
    'download_url': 'Where to download it',
    'author_email': 'carlos@hiable.com',
    'version': VERSION,
    'install_requires': ['xmltodict'],
    'tests_require': ['nose'],
    'packages': ['flatxml', 'flatxml.test'],
    'scripts': [],
    'name': 'flatxml'
}

setup(**config)
