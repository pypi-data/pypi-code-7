import os
from setuptools import setup, find_packages
from pip.req import parse_requirements

VERSION = "0.1.0dev1"

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

install_reqs = parse_requirements('requirements.txt')

setup(
    name = "batterystaple",
    version = VERSION,
    author = "Chuck Bassett",
    author_email = "iamchuckb@gmail.com",
    description = ("Small library for generating XKCD style passphrases"),
    license = "MIT",
    keywords = "passwords passphrases",
    url = "https://github.com/chucksmash/batterystaple",
    package_data = {'batterystaple': ['resources/word_list_en.txt']},
    packages= find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: Mac OS :: MaxOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2.7"
    ],
    install_requires = [str(ir.req) for ir in install_reqs],
)
