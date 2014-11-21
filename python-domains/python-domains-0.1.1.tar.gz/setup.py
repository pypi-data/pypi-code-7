
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import domains


config = {
    'description': 'Domain name utilities',
    'author': 'mrkschan',
    'url': 'https://github.com/mrkschan/python-domains',
    'download_url': 'https://github.com/mrkschan/python-domains',
    'author_email': 'mrkschan@gmail.com',
    'version': domains.__version__,
    'install_requires': ['nose'],
    'packages': ['domains'],
    'scripts': [],
    'name': 'python-domains'
}

setup(**config)
