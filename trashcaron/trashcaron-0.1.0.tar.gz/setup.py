from distutils.core import setup
setup(
    # Application name:
    name="trashcaron",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="eayin2",
    author_email="eayin2 at gmail dot com",

    scripts=["trashcaron.py"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://github.com/eayin2/trashcaron",

    #
    # license="LICENSE.txt",
    description="Trashbin script with btrfs support and automatic trash purge feature.",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[],
)
