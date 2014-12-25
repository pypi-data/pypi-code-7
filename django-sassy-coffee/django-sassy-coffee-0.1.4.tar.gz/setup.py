import os
from setuptools import setup, find_packages

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-sassy-coffee',
    version='0.1.4',
    packages=find_packages(),

    # Dependencies
    install_requires=['Django>=1.6.5', 'CoffeeScript>=1.0.9', 'csscompressor>=0.9.3', 'pyScss==1.2.0.post3', 'sassin>=0.9.2', 'slimit>=0.8.1'],

    # Metadata for PyPI
    author='Laura Manzur',
    author_email='lc.manzur@novcat.com.co',
    maintainer='Laura Manzur',
    maintainer_email='lc.manzur@novcat.com.co',
    description='This is a django application to compile SASS, SCSS and CoffeeScript files from the static directory into CSS and JavaScript files',
    long_description=README,
    license='Apache License',
    url='https://github.com/lmanzurv/sassy_coffee',
    keywords='sass coffeescript scss django',
    download_url='https://github.com/lmanzurv/sassy_coffee',
    bugtrack_url='https://github.com/lmanzurv/sassy_coffee/issues',
    classifiers=[
        'Framework :: Django',
        'License :: OSI Approved :: Academic Free License (AFL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7'
    ]
)
