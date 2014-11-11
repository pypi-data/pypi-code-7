#!/usr/bin/env python
from setuptools import setup, find_packages
 
setup (
    name = "VEP_Core",
    version = "1.01",
    description="VEP Core contains the Serendip corpus exploration tool.",
    long_description="Serendip (of VEP Core) is a tool for exploring text corpora through the use of topic modeling.",
    author="Eric Alexander",
    author_email="ealexand@cs.wisc.edu",
    license="BSD",
    #url="http://pages.cs.wisc.edu/~ealexand", # Should be the URL for downloading Serendip. Not necessary unless distributing via PyPI
    #package_dir = {'': 'src'}, # See packages below
	#include_package_data = True,
    #package_data = {'': ['.txt', '*.js', '*.json', '*.css', '*.png', '*HTML.zip'], 'templates': ['*.html']},
    #package_data = {'': ['.txt', '*.csv', '*.svg', '*.html', '*.js', '*.json', '*.css', '*.png', '*HTML.zip'], 'templates': ['*.html']},
    packages = find_packages(exclude="test"),
    # Use this line if you've uncommented package_dir above.
    #packages = find_packages("src", exclude="tests"),
 
    entry_points = {
        'console_scripts': ['serendip = vep_core:main',
                            'vep_tmbuilder = vep_core.Apps.SaliencyTopicModelerApp:main']
                   },
 
    #download_url = "http://bashelton.com/download/", # Similar deal to url
    zip_safe = False,
	install_requires=['Flask','webassets','numpy', 'scipy']
)