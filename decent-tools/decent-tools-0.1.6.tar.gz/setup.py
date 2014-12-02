from setuptools import setup, find_packages
import os

def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

setup(name='decent-tools',
    version='0.1.6',
    description='decentnode tools',
    long_description=(read('README.rst')),
    classifiers = [
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Systems Administration',
        ],
    url='http://www.decentlab.com',
    author='hashiname',
    author_email='hashiname@gmail.com',
    license='Apache License 2.0',
    packages=find_packages(exclude='tests'),
    entry_points = {
        'console_scripts': [
            'dn-bsl = dn.bsl:main',
            'dn-ftdi-cbus = dn.ftdicbus:main',
            'dn-tc65i = dn.tc65i.__main__:main',
            ],
        },
    install_requires = [
        'pyserial',
        'python_msp430_tools'
        ],
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
    )
