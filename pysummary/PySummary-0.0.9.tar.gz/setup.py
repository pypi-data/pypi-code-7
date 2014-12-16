from distutils.core import setup
from pysummary import *
setup(
    name = 'PySummary',
    packages = ['pysummary'], # this must be the same as the name above
    version = '0.0.9',
    description = 'A simple statistical summary lib',
    author = 'Zhonghua Xi',
    author_email = 'xizhonghua@gmail.com',
    url = 'https://github.com/xizhonghua/pysummary', # use the URL to the github repo
    download_url = 'https://github.com/xizhonghua/pysummary/tarball/0.0.9', # I'll explain this in a second
    keywords = ['stats', 'statistical', 'summary', 'mean', 'confidential interval'], # arbitrary keywords
    classifiers = [],
)