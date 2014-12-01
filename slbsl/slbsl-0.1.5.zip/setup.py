# :coding: utf-8
import os
import setuptools

requirements = os.path.join(os.path.dirname(__file__), "requirements.txt")

setuptools.setup(
    name="slbsl",
    version="0.1.5",
    description="Convert slashes in text on commandline or in clipboard.",
    long_description=open("README.rst").read(),
    keywords="slash, backslash, linux, unix, windows, conversion",
    url="https://cb109@bitbucket.org/cb109/slbsl.git",
    author="Christoph Buelter",
    author_email="c.buelter@arcor.de",
    packages=setuptools.find_packages(),
    include_package_data = True,
    install_requires=[
        open(requirements).readlines()
    ],
    entry_points={
        "console_scripts": [
            "sl=slbsl:sl",
            "bsl=slbsl:bsl"
        ],
    }
)

