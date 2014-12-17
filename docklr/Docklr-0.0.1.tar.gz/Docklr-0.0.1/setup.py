__author__ = 'drichner'
"""
Docklr
------

A web front end for Docker and Fleet.

"""
from setuptools import setup


setup(
    name='Docklr',
    version='0.0.1',
    url='https://github.com/drichner/docklr',
    license='GPLv2',
    author='Dan Richner',
    author_email='drichner@candidsolution.net',
    description='A web front end for Docker and Fleet.',
    long_description=__doc__,
    py_modules=['docklr'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'Flask >= 0.10',
        'Flask-Bootstrap==3.3.0.1'
    ],
    test_suite='test_docklr.suite',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)