import re
from setuptools import setup
#from distutils.core import setup

VERSIONFILE="GoreUtilities/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^version = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    version = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name = 'GoreUtilities',
    packages = ['GoreUtilities', 'GoreUtilities.test'], # this must be the same as the name above
    version = version,
    description = 'Some utility functions useful for GoreLab members',
    author = 'Eugene Yurtsev, Jonathan Friedman',
    author_email = 'eyurtsev@mit.edu',
    url = 'https://bitbucket.org/gorelab/goreutilities/',
    download_url = 'https://bitbucket.org/gorelab/goreutilities/get/v{0}.zip'.format(version),
    keywords = ['utility', 'plot', 'gorelab'],
    license='MIT',
    #install_requires=[
          #"pandas >= 0.8.0",
      #],
)
