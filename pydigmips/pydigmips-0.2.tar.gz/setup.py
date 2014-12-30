#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='pydigmips',
    version='0.2',
    description='DigMIPS interpreter.',
    url='https://github.com/ProjetPP/pydigmips',
    author='Valentin Lorentz',
    author_email='valentin.lorentz+ppp@ens-lyon.org',
    license='MIT',
    classifiers=[
        'Environment :: Console',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Assemblers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
    ],
    install_requires=[
    ],
    packages=[
        'pydigmips',
    ],
)


