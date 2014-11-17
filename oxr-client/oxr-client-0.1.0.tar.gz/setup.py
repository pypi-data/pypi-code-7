from setuptools import setup, find_packages

setup(
    name = 'oxr-client',
    version = '0.1.0',
    description = "A client for open exchange rates",
    url = 'https://github.com/jcomo/oxr-client',
    author = 'Jonathan Como',
    author_email = 'jonathan.como@gmail.com',
    packages = find_packages(exclude=['docs', 'tests']),
    install_requires = ['requests'],
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ],
    keywords = 'development client open exchange rates'
)
