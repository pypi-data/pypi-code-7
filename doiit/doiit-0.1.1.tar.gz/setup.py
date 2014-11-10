import os
from setuptools import setup, find_packages

# package meta info
NAME = "doiit"
VERSION = "0.1.1"
DESCRIPTION = ""
AUTHOR = "Haochuan Guo"
AUTHOR_EMAIL = "guohaochuan@gmail.com"
LICENSE = "BSD"
URL = "https://github.com/wooparadog/doiit"
REQUIREMENTS = ["click"]
ENTRY_POINTS = [
    "doiit = doiit:root",
]


# package contents
PACKAGES = find_packages(
    exclude=['tests.*', 'tests', 'examples.*', 'examples',
             'dev_requirements.txt'])

here = os.path.abspath(os.path.dirname(__file__))

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    install_requires=REQUIREMENTS,
    license=LICENSE,
    url=URL,
    packages=PACKAGES,
    install_package_data=True,
    entry_points={"console_scripts": ENTRY_POINTS},
    zip_safe=False,
)
