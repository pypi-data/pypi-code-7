#!/usr/bin/python

from distutils.core import setup

setup(
    name = 'openBrowser',
    packages = ['openBrowser'],
    version = '0.0.2',
    description = 'A CLI helper to quick open file/url with browser in command line',
    license='LICENSE',
    author = 'lufeng',
    author_email = 'lufengd3@gmail.com',
    url = 'https://github.com/keith3/myPip/tree/master/openBrowser',
    # download_url = 'https://github.com/keith3/myPip/openBrowser', 
    keywords = ['browser', 'cli'],
    classifiers = [],
    entry_points = {
        'console_scripts': [
            'open = openBrowser.main:main',    
        ]
    },
)
