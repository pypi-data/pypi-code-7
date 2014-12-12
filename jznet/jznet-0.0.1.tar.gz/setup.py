import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='jznet',
    version='0.0.1',
    keywords=('net', 'websocket', 'RPC',),
    description='a python RPC library based on websocket',
    long_description=read('README.md'),
    license='MIT License',
    install_requires=['gevent', 'gevent-websocket'],
    author='zoowii',
    author_email='1992zhouwei@gmail.com',
    packages=find_packages(exclude=['*test']),
    platforms='any',
)