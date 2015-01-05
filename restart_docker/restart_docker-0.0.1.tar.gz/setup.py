from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='restart_docker',

    version='0.0.1',

    description='A tool for restarting docker containers if their configuration or base image changes.',
    long_description=long_description,

    url='https://github.com/albertkoch/restart_docker',

    author='Albert Koch',
    author_email='kocha@slagit.net',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
    ],

    packages=find_packages(),

    install_requires=['docker_py'],

    entry_points={
        'console_scripts': [
            'restart_docker=restart_docker:main',
        ],
    },
)

# vim:sw=4 expandtab
