#coding=utf-8
import os
from setuptools import setup

def openf(fname):
    return open(os.path.join(os.path.dirname(__file__), fname))

setup(
    name="sqltocache",
    version="1.0",
    author="fengyun.rui",
    author_email="rfyiamcool@163.com",
    description="result of sql cache to redis",
    url="https://github.com/rfyiamcool",
    packages=['sqltocache'],
    long_description=openf("README.md").read(),
    install_requires=[line.strip() for line in openf("requirements.txt") if line.strip()],
)
