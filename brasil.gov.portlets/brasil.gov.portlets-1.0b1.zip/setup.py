# -*- coding:utf-8 -*-

from setuptools import find_packages
from setuptools import setup

version = '1.0b1'
description = 'Portlets para Portal Padrão'
long_description = (
    open('README.rst').read() + '\n' +
    open('CONTRIBUTORS.rst').read() + '\n' +
    open('CHANGES.rst').read()
)

setup(
    name='brasil.gov.portlets',
    version=version,
    description=description,
    long_description=long_description,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='plonegovbr portlets brasil plone',
    author='PloneGovBr',
    author_email='gov@plone.org.br',
    url='https://github.com/plonegovbr/brasil.gov.portlets',
    license='GPLv2',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['brasil', 'brasil.gov'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'five.pt',
        'plone.api',
        'plone.app.upgrade',
        'Products.CMFPlone >=4.3',
        'Products.GenericSetup',
        'sc.embedder',
        'setuptools',
        'zope.i18nmessageid',
        'zope.interface',
    ],
    extras_require={
        'test': [
            'brasil.gov.portal',
            'plone.app.contenttypes<1.1a1',
            'plone.app.dexterity',
            'plone.app.robotframework',
            'plone.app.testing [robot] >=4.2.2',
            'plone.browserlayer',
            'plone.testing',
        ],
    },
    entry_points="""
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
