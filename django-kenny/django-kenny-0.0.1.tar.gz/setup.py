import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

from kenny import __version__

setup(
    name = "django-kenny",
    version = __version__,
    author = "Tomas Neme",
    author_email = "lacrymology@gmail.com",
    description = ("An extremely simple TemplateView for django"),
    license = "MIT",
    keywords = "django generic-views",
    url = "https://github.com/Lacrymology/django-kenny",
    packages=['kenny'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)

