#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages


Name='ua2.carbon'
ProjecUrl="https://bitbucket.org/ua2crm/ua2.carbon"
Version='0.0.4'
Author='Vic'
AuthorEmail='vic@ua2web.com'
Maintainer='Viacheslav Vic Bukhantsov'
Summary='Tool for stream statistics to carbon daemon (from graphite)'
License='BSD License'
ShortDescription=Summary

with open('README.rst') as fh:
    long_description = fh.read()

needed = [
]

EagerResources = [
    'ua2',
]

ProjectScripts = [
##    'scripts/runweb',
]

PackageData = {
    '': ['*.*', '*.html'],
}

# Make exe versions of the scripts:
EntryPoints = {
}

setup(
    url=ProjecUrl,
    name=Name,
    zip_safe=False,
    version=Version,
    author=Author,
    author_email=AuthorEmail,
    description=ShortDescription,
    long_description=long_description,
    license=License,
    scripts=ProjectScripts,
    install_requires=needed,
    include_package_data=True,
    packages=find_packages('src'),
    package_data=PackageData,
    package_dir = {'': 'src'},
    eager_resources = EagerResources,
    entry_points = EntryPoints,
    namespace_packages = ['ua2'],
)
