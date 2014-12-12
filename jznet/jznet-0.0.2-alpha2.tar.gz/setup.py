import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()


setup(
    name='jznet',
    version='0.0.2-alpha2',
    keywords=('net', 'websocket', 'RPC',),
    description='a python RPC library based on websocket',
    long_description="""
pyjznet
====
python implementation of jznet

## Requirements

You need install gevent and gevent-websocket manually

* gevent
* gevent-websocket

## Install

pip install jznet

## Usage

    >>> import pyjznet
    >>> from pyjznet import Server
    >>> class DemoService(object):
            def sayHi(self, name, remote_service):
                try:
                    age = remote_service.call_rpc('demo', 'getAge')
                except Exception as e:
                    logging.error(e)
                    return str(e)
                logging.info('got say hi request of %s who\'s age is %d' % (name, age))
                return "Hi, %s who's age is %d!" % (name, age)
    >>> server = Server()
    >>> server.add_rpc_service('demo', DemoService())
    >>> server.start()

call the service using jznet.js library
    """,
    license='MIT License',
    install_requires=[],
    author='zoowii',
    author_email='1992zhouwei@gmail.com',
    packages=find_packages(exclude=['*test']),
    platforms='any',
)