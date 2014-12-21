#!/usr/bin/env python3
from setuptools import setup

with open("README.rst") as fd:
    long_description = fd.read()

setup(
    name="postie",
    version="1.1.1",
    description="Simple Python library to manage SMTP configurations.",
    long_description=long_description,
    author="Tom Leese",
    author_email="inbox@tomleese.me.uk",
    url="https://github.com/tomleese/postie",
    packages=["postie"],
    install_requires=[
        "jinja2"
    ],
    classifiers=[
        "Topic :: Internet",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ]
)
