import os 
from setuptools import (
    setup, 
    find_packages
    )

name="whtc.recipe.configmanager"
version = '1.0rc1'
tests_require=[
    'zope.testing', 
    'zc.buildout',
    'collective.recipe.template', 
    ]

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

setup(
    name=name,
    keywords='config configuration recipe buildout template',
    version=version,
    description=(
        "A buildout recipe to manage auto-populating portions of shared "
        "configuration files that cannot simply overwritten."
        ),
    long_description=(
        read('README.txt')
        + '\n' +
        read('whtc', 'recipe', 'configmanager', 'README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Download\n'
        '********\n'
        ),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Buildout :: Recipe",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python",
        "Topic :: System :: Software Distribution",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    author='Hugh T. Ranalli',
    author_email='hugh@whtc.ca',
    url='http://pypi.python.org/pypi/whtc.recipe.configmanager',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['whtc', 'whtc.recipe' ],
    include_package_data=True,
    zip_safe=True,
    install_requires=[
        'setuptools',
        'zc.buildout',
        'collective.recipe.template',
        ],
    tests_require=tests_require,
    extras_require={
        'test' : tests_require,
        'templates' : ['collective.recipe.template', ],
        },
    
    test_suite='%s.tests.test_suite' % name,
    entry_points={
        'zc.buildout': ['default = %s:Recipe' % name],
        'zc.buildout.uninstall': ['default = %s:uninstall' % name],
        },
      )
