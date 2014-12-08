import re
from setuptools import setup

init_py = open('pyconza2014/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
metadata['doc'] = re.findall('"""(.+)"""', init_py)[0]

setup(
    name='pyconza2014',
    version=metadata['version'],
    description=metadata['doc'],
    author=metadata['author'],
    author_email=metadata['email'],
    url=metadata['url'],
    packages=['pyconza2014'],
    include_package_data=True,
    install_requires=[
        'click < 2.1.0'
    ],
    entry_points={
        'console_scripts': [
            'pyconza2014 = pyconza2014.cli:main',
        ],
    },
    test_suite='nose.collector',
    license=open('LICENSE').read(),
)
