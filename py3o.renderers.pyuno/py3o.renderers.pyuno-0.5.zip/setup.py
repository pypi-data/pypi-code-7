# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.5'


def read(filename):
    with open(filename, "r") as f:
        return f.read()

setup(
    name='py3o.renderers.pyuno',
    version=version,
    description="A pyuno based driver for py3o",
    long_description="{0}\n{1}\n{2}".format(
        read("README.rst"),
        read("CHANGES.rst"),
        read("CONTRIBUTORS.rst"),
    ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='OpenOffice PDF',
    author='Florent Aide',
    author_email='florent.aide@gmail.com',
    url='https://bitbucket.org/faide/py3o.renderers.pyuno',
    license='MIT License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['py3o'],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        read("requirements.txt")
    ],
    entry_points=dict(
        # -*- Entry points: -*-
    ),
    test_suite='nose.collector',
)
