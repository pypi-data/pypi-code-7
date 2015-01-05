# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


version = '0.1'

long_description = (
    read('README.rst')
    + '\n' +
    read('docs/HISTORY.rst')
    + '\n' +
    read('CONTRIBUTORS.rst')
    )

setup(
    name='collective.ruleactions.pythonscript',
    version=version,
    description="",
    long_description=long_description,
    # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    keywords='',
    author='Florian Schulze',
    author_email='florian.schulze@gmx.net',
    url='https://github.com/collective/collective.ruleactions.pythonscript',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.ruleactions'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'setuptools',
        ],

    entry_points={
        # -*- Entry points: -*-
        'z3c.autoinclude.plugin': 'target = plone',
        },
    )
