from setuptools import setup, find_packages

VERSION = "1.0.0"

LONG_DESCRIPTION = """
=================================
django-advert
=================================
Django Advert is a small module that will allow developers to create advertisement
models.
"""

setup(
    name='django-advert',
    version=VERSION,
    url='https://github.com/koralarts/django-advert',
    download_url='https://github.com/koralarts/django-advert/tarball/1.0.0.tar.gz',
    description='A small module that will allow developers to create advertisement models.',
    long_description=LONG_DESCRIPTION,
    author='Karl Castillo',
    author_email='karl@karlworks.com',
    maintainer='Karl Castillo',
    maintainer_email='karl@karlworks.com',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management'
    ],
    keywords=['django','advertisement','utility'],
    packages=[
        'advert',
        'advert.tests'
    ],
    install_requires=[
        'django>=1.7',
        'Pillow'
    ]
)
