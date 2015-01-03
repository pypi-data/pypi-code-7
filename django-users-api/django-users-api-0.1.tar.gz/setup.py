from setuptools import setup, find_packages

from users_api import __VERSION__

try:
    # For development.
    from setuptest import test
    CMDCLASS = {'test': test}
except ImportError:
    CMDCLASS = {}


setup(
    name='django-users-api',
    version=__VERSION__,
    description='Django users RESTful API using Tastypie.',
    long_description=open('README.rst').read(),
    author='Mohab Usama',
    author_email='mohab.usama@gmail.com',
    url='https://github.com/mohabusama/django-users-api',
    packages=find_packages(exclude=['tests']),
    license=open('LICENSE').read(),
    zip_safe=False,
    tests_require=(
        'django-setuptest', 'django>=1.4', 'django-tastypie>=0.12.1'),
    test_suite='setuptest.setuptest.SetupTestSuite',
    cmdclass=CMDCLASS,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
