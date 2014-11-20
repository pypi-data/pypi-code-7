from __future__ import print_function
from setuptools import setup

version = "0.7.1"

print(version)

description = \
"""Common API for reading and writing soundfiles.   
* Uses installed packages if found (scikits.audiolab)  
* Implements reading uncompressed formats correctly in any format.  
* The data is independent of the encoding. All data is presented as float64  
* Bitdepth is handled automatically depending on the the actual data  
"""

setup(
    name         = "sndfileio",
    version      = version,
    description  = description,
    summary      = "Simple API for reading and writing soundfiles", 
    author       = "Eduardo Moguillansky",
    author_email = "eduardo moguillansky dot gmail dot com",
    url          = "https://github.com/gesellkammer/sndfileio",
    packages     = [ "sndfileio"],
    package_data = {'': ['README.md']},
    include_package_data = True,
    install_requires     = [
        "numpy>1.5"
    ]
)
