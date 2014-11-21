
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'qmi(quant library from mirib)',
    'author': 'HongSeokHwan',
    'url': 'https://github.com/HongSeokHwan/qmi.git',
    'author_email': 'madusin@naver.com',
    'version': '0.1',
    'install_requires': [],
    'packages': ['qmi'],
    'scripts': [],
    'name': 'qmi'
}

setup(**config)
