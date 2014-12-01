from setuptools import setup
from os import path

with open(path.join(path.dirname(__file__), 'README.md')) as readme:
  long_description = readme.read()


setup(
  name="PyJOAT",
  version="1.1.1",
  author="R. Kevin Nelson",
  author_email="kevin@rkn.la",
  description="JWT OAuth 2.0 Access Token management",
  license="MIT",
  keywords="joat jwt json web access token oauth",
  url="https://github.com/rknLA/joat",
  packages=['joat'],
  long_description=long_description,
  install_requires=['PyJWT'],
  classifiers=[
    "Environment :: Web Environment",
    "Intended Audience :: Developers",
    "Development Status :: 3 - Alpha",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2.7",
    "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    "Topic :: Software Development :: Libraries :: Python Modules"
  ]
)
