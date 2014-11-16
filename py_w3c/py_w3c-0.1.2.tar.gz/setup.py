from distutils.core import setup

from setuptools import find_packages

setup(
    name='py_w3c',
    version='0.1.2',
    author='Kazbek Byasov',
    author_email='nmb.ten@gmail.com',
    packages=find_packages(),
    url='http://pypi.python.org/pypi/py_w3c/',
    license='LICENSE.txt',
    description='W3C services for python.',
    long_description=open('README.txt').read(),
    install_requires=[],
    entry_points={
        'console_scripts':
            ['w3c_validate = py_w3c.validators.html.validator:main']
    }
)
