from setuptools import *

setup(
    # Metadata
    name="todot",
    version="0.1",
    author="Calder Coalson",
    author_email="caldercoalson@gmail.com",
    url="https://github.com/calder/todot",
    description="Simple todo list task dependency dotfile generator.",
    long_description="See https://github.com/calder/todot/ for documentation.",
    license="LICENSE.txt",

    # Contents
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "todot=todot:main",
        ],
    },

    # Dependencies
    install_requires=[
    ],

    # Settings
    zip_safe=True,
)