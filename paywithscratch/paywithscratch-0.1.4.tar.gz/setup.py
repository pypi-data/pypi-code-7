from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.txt'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='paywithscratch',
    version='0.1.4',
    description='Scratch Payment Library',
    long_description=long_description,
    url='https://github.com/paywithscratch/',
    author='Mu, LLC',
    author_email='eric@paywithscratch.com',
    license='MIT',
    keywords='scratch online payments',
    packages=['scratch'],
    install_requires=['scratch-openid'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial :: Point-Of-Sale',
    ],
)
