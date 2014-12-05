import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='ahonya-sika',
    version='0.1.1',
    description='Sika API library client for python',
    author='Philip Adzanoukpe',
    author_email='philip@ahonya.com',
    url='https://github.com/Ahonya/sika-python',
    license='MIT',
    install_requires=[
        'requests >= 2.1.0',
        'simplejson >=3.6.5'
    ],
    packages=[
        'sika'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
