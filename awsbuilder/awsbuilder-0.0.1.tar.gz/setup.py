from setuptools import setup

setup(
    # Application name:
    name="awsbuilder",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="Stuart Munro",
    author_email="stuart.munro@digital.justice.gov.uk",

    # Packages
    packages=["awsbuilder"],

    # Executables
    scripts=['awsbuilder/bin/awsbuilder'],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/ministryofjustice/awsbuilder",

    #
    # license="LICENSE.txt",
    description="Command line tools top create AWS objects based on a config file",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "boto==2.34.0",
        "PyYAML==3.11"
    ],

    license = "MIT",

    platforms = "Posix; MacOS X",

    classifiers = ["Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Topic :: Internet",
                   "Programming Language :: Python :: 2",
                   "Programming Language :: Python :: 2.6",
                   "Programming Language :: Python :: 2.7"],
)