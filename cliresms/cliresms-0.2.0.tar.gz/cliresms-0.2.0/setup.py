from setuptools import setup, find_packages
from os import path


setup(
    name='cliresms',
    version='0.2.0',
    description='A script to send webtexts from the command line for Irish carriers',
    url='https://github.com/russelldavies/cliresms',
    author='Russell Davies',
    license='Apache v2',
    keywords='console cli sms webtext',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[],
    extras_require = {
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    entry_points={
        'console_scripts': [
            'cliresms=cliresms:main',
        ],
    },
)
