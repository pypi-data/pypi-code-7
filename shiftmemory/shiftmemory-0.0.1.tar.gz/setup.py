import os
from setuptools import setup, find_packages


version = '0.0.1'


# monkey patch os for vagrant hardlinks
del os.link


# prepare config
config = dict(

    # author
    author = 'Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name = 'shiftmemory',
    version=version,
    url = 'https://github.com/projectshift/shift-memory',
    download_url='https://github.com/projectshift/shift-memory/tarball/'+version,
    description='Python3 cache library',
    keywords=['python3', 'cache', 'redis', 'memcached'],

    # license
    license = 'MIT',

    # packages
    packages = find_packages(exclude=['tests']),

    # dependencies
    install_requires = [
        'redis==2.10.3',
        'hiredis==0.1.5',
        'arrow==0.4.4'
    ]

)

# finally run the setup
setup(**config)