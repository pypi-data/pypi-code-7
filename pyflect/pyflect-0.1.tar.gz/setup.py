__author__ = 'bagrat'

from setuptools import setup, find_packages

tests_require = ['nose', 'coverage']

install_requires = []

config = {
    'description': 'Put on your Java suit and go get_methods',
    'author': 'Bagrat Aznauryan',
    'url': 'https://github.com/n9code/pyflect',
    'download_url': 'https://github.com/n9code/pyflect',
    'author_email': 'bagrat@aznauryan.org',
    'version': '0.1',
    'install_requires': install_requires,
    'tests_require': tests_require,
    'packages': find_packages(),
    'name': 'pyflect'
}

setup(**config)