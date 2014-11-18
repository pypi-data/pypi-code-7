# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='teleinfo',
    version='1.0.2',
    description='EDF Teleinfo frame acquisition',
    long_description="Read and parse teleinfo data from France EDF electricity provider",
    author='Mickael Le Baillif',
    author_email='mickael.le.baillif@gmail.com',
    url='https://code.google.com/p/house-on-wire/',
    license='LICENSE',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=['pyserial'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Topic :: Home Automation",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    entry_points= {
        'console_scripts': [
            'teleinfo_json=teleinfo.utils:frame_to_json'
        ]
    }
)
