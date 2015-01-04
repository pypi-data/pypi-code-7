""" Packaging for multilogger_collectd """

import io
import os
import re

from setuptools import setup


def read(*names, **kwargs):
    """ Read file relative to the directory where this file is located """
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


def find_version(*file_paths):
    """ Get version number from file """
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


VERSION = find_version('multilogger_collectd.py')
URL = 'https://github.com/pka/arexx-multilogger-collectd-plugin'
setup(
    name='multilogger_collectd',
    version=VERSION,
    py_modules=['multilogger_collectd'],
    license='GPLv2',
    description='A collectd plugin for monitoring AREXX Multiloggers',
    long_description=read('README.rst'),
    author='Pirmin Kalberer',
    author_email='pka@sourcepole.ch',
    url=URL,
    download_url='%s/archive/multilogger_collectd-%s.tar.gz' % (URL, VERSION),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: System :: Monitoring',
    ],
    keywords='AREXX multilogger collectd',
    install_requires=[
        'pyusb'
    ],
)
