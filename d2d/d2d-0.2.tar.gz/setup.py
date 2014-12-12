import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = "d2d",
    version = "0.2",
    packages = ["d2d"],
    include_package_data=True,
    license = "BSD License",
    description = "Deploy Django application on desktop window.",
    long_description = README,
    url = "",
    author = "Yeison Cardona",
    author_email = "yeison.eng@gmail.com",
    classifiers = [
        "Environment :: Web Environment",
        "Framework :: Django",
    ],
)
