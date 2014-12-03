# setup.py ###
#from distutils.core import setup
from setuptools import find_packages, setup
import os

NAME = "check_nscp"
VERSION = "0.1.1"
SHORT_DESC = "General purpose client for talking with NSclient++"
LONG_DESC = """ """

datafiles = []

if __name__ == "__main__":
    manpath = "share/man/man1/"
    etcpath = "/etc/%s" % NAME
    etcmodpath = "/etc/%s/modules" % NAME
    initpath = "/etc/init.d/"
    logpath = "/var/log/%s/" % NAME
    varpath = "/var/lib/%s/" % NAME
    rotpath = "/etc/logrotate.d"
    datarootdir = "/usr/share/%s" % NAME
    setup(
        name='%s' % NAME,
        version=VERSION,
        author='Pall Sigurdsson',
        description=SHORT_DESC,
        long_description=LONG_DESC,
        author_email='palli@opensource.is',
        url='http://github.com/palli/check_nscp',
        license='GPL',
        scripts=['check_nscp'],
        packages=find_packages(),
        requires=['pynag'],
    )
