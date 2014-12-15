# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

long_desc = '''
This package contains the seqansphinx Sphinx extension.
'''

requires = ['Sphinx>=0.6']

setup(
    name='seqansphinx',
    version='0.3.0',
    url='http://github.com/seqan/seqan-sphinx',
    download_url='http://pypi.python.org/pypi/seqansphinx',
    license='MIT',
    author='Manuel Holtgrewe',
    author_email='manuel.holtgrewe@fu-berlin.de',
    description='Sphinx extension for SeqAn Sphinx document',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['seqansphinx'],
)
