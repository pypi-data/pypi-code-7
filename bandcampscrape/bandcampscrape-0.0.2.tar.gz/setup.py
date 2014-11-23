import os
from setuptools import setup

# Set external files
README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='bandcampscrape',
    version='0.0.2',
    packages=['bandcampscrape'],
    install_requires=required,
    include_package_data=True,
    license='MIT License',
    description='Downloader for BandCamp albums ',
    long_description=README,
    url='https://github.com/ronier/bandcampscrape',
    author='Ronier Lopez',
    author_email='ronier@gmail.com',
    entry_points={
        'console_scripts': [
            'bandcampscrape = bandcampscrape.bandcampscrape:main',
        ]
    },
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
