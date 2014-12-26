from distutils.core import setup

setup(
    name = "snail",
    packages = ["snail"],
    version = "0.0.1",
    description = "This library is for the composition and decomposition of midi files",
    author = "Stephen J. Zabel",
    author_email = "sjzabel@gmail.com",
    url = "https://github.com/sjzabel/snail",
    keywords = ["midi",],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Development Status :: 1 - Planning",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        ],
    long_description = """
Snail
--------------------------------


This is module that contains the rudimentary pieces of midi
as well as the ability to decompose and compose midi files.

The intent is to create a low-level library for working with midi files
that can be used by other programs to do more interesting things.


Credits
--------------------------------


Most of what I know comes from reading the source of several projects.
 - https://github.com/vishnubob/python-midi
 - http://www.mellowood.ca/mma/


This version requires Python 3 or later.
"""
)
