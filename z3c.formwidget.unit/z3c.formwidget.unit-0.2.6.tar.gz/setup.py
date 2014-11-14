# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = '0.2.6'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst'))

setup(
    name='z3c.formwidget.unit',
    version=version,
    description="A multi unit widget for z3c.form.",
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Zope3",
        "Intended Audience :: Other Audience",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Zope",
    ],
    keywords='zope zope3 z3c.form',
    author='Thomas Massmann',
    author_email='thomas.massmann@it-spir.it',
    url='https://github.com/tmassman/z3c.formwidget.unit',
    download_url='http://pypi.python.org/pypi/z3c.formwidget.unit',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['z3c', 'z3c.formwidget'],
    zip_safe=False,
    include_package_data=True,
    extras_require=dict(
        fanstatic=[
            'js.bootstrap_select',
        ],
        test=[
            'unittest2',
            'z3c.form [test]',
            'zc.buildout',
            'zope.browserpage',
            'zope.publisher',
            'zope.testing',
            'zope.traversing',
        ],
    ),
    install_requires=[
        'setuptools',
        'pint',
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    message_extractors={"src": [
        ('**.py', 'lingua_python', None),
        ('**.pt', 'lingua_xml', None),
    ]},
)
