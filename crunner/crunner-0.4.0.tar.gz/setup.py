# -*- coding: utf-8 -*-
from setuptools import setup


requires = [
    'mock==1.0.1',
    'watchdog==0.7.1',
]


setup(
    name="crunner",
    version="0.4.0",
    packages=['crunner'],
    author="Pawel Chomicki",
    author_email="pawel.chomicki@gmail.com",
    description="Continues test runner.",
    url="http://pchomik.github.io/crunner/",
    install_requires=requires,
    include_package_data=True,
    scripts=['script/crun']
)
