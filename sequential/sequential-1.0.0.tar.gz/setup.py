from distutils.core import setup

setup(
    name="sequential",
    packages=["sequential"],
    version="1.0.0",
    description="Sequential wrappers for python functions.",
    author="Phil Condreay",
    author_email="0astex@gmail.com",
    url="https://github.com/astex/sequential",
    keywords=["functions", "decorators", "multithreading", "convenience"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules"
        ],
    long_description="""\
Sequential
-----
Sequential wrappers for python functions allowing you to easily define order of
execution independent of content of the function.
"""
)
