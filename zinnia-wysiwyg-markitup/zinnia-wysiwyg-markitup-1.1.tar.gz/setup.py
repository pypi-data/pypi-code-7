"""Setup script of zinnia-wysiwyg-markitup"""
from setuptools import setup
from setuptools import find_packages

import zinnia_markitup

setup(
    name='zinnia-wysiwyg-markitup',
    version=zinnia_markitup.__version__,

    description='MarkItUp for editing entries in django-blog-zinnia',
    long_description=open('README.rst').read(),

    keywords='django, zinnia, wysiwyg, markitup',

    author=zinnia_markitup.__author__,
    author_email=zinnia_markitup.__email__,
    url=zinnia_markitup.__url__,

    packages=find_packages(exclude=['demo_zinnia_markitup']),
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

    license=zinnia_markitup.__license__,
    include_package_data=True,
    zip_safe=False
)
