#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

requires = [
    'tornado',
    'numpy',
]

setup(
    name='Mesa',
    version=0.5,
    description='Agent-based modeling framework in Python.',
    #long_description=readme + '\n\n' + history,
    author='Project Mesa Team',
    author_email='projectmesa@googlegroups.com',
    url='https://github.com/projectmesa/mesa',
    packages=['mesa'],
    package_data={'': ['LICENSE.md', ], },
    package_dir={'mesa': 'mesa'},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Topic :: Scientific/Engineering',
    ),
)
