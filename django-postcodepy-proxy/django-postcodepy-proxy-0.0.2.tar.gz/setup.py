import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = map(str.strip, open("requirements.txt").readlines())

setup(
    name = "django-postcodepy-proxy",
    version = "0.0.2",
    author = "Feite Brekeveld",
    author_email = "f.brekeveld@gmail.com",
    description = ("simple Django app to make your backend serve as a proxy for postcode.nl REST-API"),
    license = "MIT",
    keywords = "postcode.nl REST API django proxy python",
    url = "https://github.com/hootnot/django-postcodepy-proxy",
    packages=['postcodepy_proxy', 'tests'],
    install_requires = requirements,
    #package_data = { }
    #include_package_data = True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    test_suite="tests",
)

