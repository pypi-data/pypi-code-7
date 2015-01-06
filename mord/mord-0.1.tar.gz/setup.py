from setuptools import setup, find_packages

setup(name='mord',
    version='0.1',
    description=open('README.rst').read(),
    author='Fabian Pedregosa',
    author_email='f@bianp.net',
    url='',
    packages=['mord'],
    requires = ['numpy', 'scipy'],
)
