

import os
from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-dynamic-models',
    version='0.0.5',
    packages=['django_dynamic_models'],
    include_package_data=True,
    license='BSD License',
    description='A Django app that enable change model fields if other other apps models',
    long_description=README,
    url='https://pypi.python.org/pypi/django-dynamic-models',
    author='Jesus Manuel Herrera Miramontes',
    author_email='jesusmaherrera@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)

class upload:
  shared_options = {'register': ['repository']}