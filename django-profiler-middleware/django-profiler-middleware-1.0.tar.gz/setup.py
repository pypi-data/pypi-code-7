from setuptools import setup, find_packages
import os

from django_profiler import __version__

file_dir = os.path.abspath(os.path.dirname(__file__))


def read_file(filename):
    with open(os.path.join(file_dir, filename), 'r') as f:
        return f.read()


setup(
    name="django-profiler-middleware",
    version=__version__,
    description=('A profiler middleware for Django'),
    long_description=read_file('README.rst'),
    author='mySociety',
    author_email='matthew@mysociety.org',
    url='https://github.com/mysociety/django-profiler-middleware',
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Topic :: Database :: Front-Ends',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
