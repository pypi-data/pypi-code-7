from setuptools import find_packages

import sys as _sys
pyver = float('%s.%s' % _sys.version_info[:2])

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

try:
    readme = open('README.rst').read()
except IOError:
    readme = ''
    
install_requires = ['PyJWT == 0.2.1', 'requests >= 2.2.1', 'python-dateutil == 2.2']

if pyver < 2.7:
    install_requires.append('ordereddict == 1.1')
    
if pyver < 3.4:
    install_requires.append('enum34 == 1.0')

setup(
    name='livefyre',
    cmdclass={'build_py': build_py},
    version='2.0.2',
    description='Livefyre Python utility classes',
    long_description=readme,
    license='MIT',
    keywords='livefyre',
    author='Livefyre',
    author_email='tools@livefyre.com',
    url='http://livefyre.com/',
    packages=find_packages(),
    install_requires=install_requires,
    test_suite='livefyre.tests',
    use_2to3=True,
    zip_safe=True,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ])