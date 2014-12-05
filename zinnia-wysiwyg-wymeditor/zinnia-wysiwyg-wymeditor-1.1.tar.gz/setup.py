"""Setup script of zinnia-wysiwyg-wymeditor"""
from setuptools import setup
from setuptools import find_packages

import zinnia_wymeditor

setup(
    name='zinnia-wysiwyg-wymeditor',
    version=zinnia_wymeditor.__version__,

    description='WYMEditor for editing entries in django-blog-zinnia',
    long_description=open('README.rst').read(),

    keywords='django, zinnia, wysiwyg, wymeditor',

    author=zinnia_wymeditor.__author__,
    author_email=zinnia_wymeditor.__email__,
    url=zinnia_wymeditor.__url__,

    packages=find_packages(exclude=['demo_zinnia_wymeditor']),
    classifiers=[
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license=zinnia_wymeditor.__license__,
    include_package_data=True,
    zip_safe=False
)
