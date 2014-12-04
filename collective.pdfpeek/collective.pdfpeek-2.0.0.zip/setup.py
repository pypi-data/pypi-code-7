from setuptools import setup, find_packages

import os


def read(*paths):
    return open(os.path.join(os.path.dirname(__file__), *paths), 'r').read()

version = '2.0.0'

setup(
    name='collective.pdfpeek',
    version=version,
    description="A Plone 4 product that generates image thumbnail previews " +
                "of PDF files stored on ATFile based objects.",
    long_description="\n\n".join([
        read("README.rst"),
        read("docs", "TODO.rst"),
        read("docs", "INSTALL.rst"),
        read("docs", "CHANGES.rst"),
    ]),
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='Plone Zope Python PDF',
    author='David Brenneman',
    author_email='db@davidbrenneman.com',
    url='https://github.com/collective/collective.pdfpeek',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'PyPDF2',
        'plone.app.registry',
        'plone.browserlayer',
        'plone.rfc822',
        'Pillow',
        'plone.api',
    ],
    extras_require={
        'archetype': [
            'Products.Archetypes',
            'Products.ATContentTypes'
        ],
        'dexterity': [
            'plone.behavior',
            'plone.app.contenttypes >= 1.0rc1'
        ],
        'zamqp': [
            'msgpack-python',
            'collective.zamqp >= 0.12.0',
        ],
        'test': [
            'Products.ATContentTypes',
            'msgpack-python',
            'plone.app.contenttypes',
            'plone.app.testing',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
