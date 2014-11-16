import os
from setuptools import setup
import taxonomy

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django_taxonomy',
    version=taxonomy.__version__,
    packages=['taxonomy'],
    include_package_data=True,
    license='LGPL',
    description='Taxonomy Model to use for django categories',
    long_description=README,
    url='http://www.ohmypixel.com/',
    author='George Georgiou',
    author_email='george@ohmypixel.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'django-mptt',
        'django',
    ],
)
