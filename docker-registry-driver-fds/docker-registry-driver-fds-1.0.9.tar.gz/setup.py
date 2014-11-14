#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import setuptools
except ImportError:
    import distutils.core as setuptools

__author__ = 'tobe'
__copyright__ = 'Copyright 2014'
__credits__ = []

__license__ = 'Apache 2.0'
__version__ = '1.0.9'
__maintainer__ = 'tobe'
__email__ = 'tobeg3oogle@gmail.com'
__status__ = 'Production'

__title__ = 'docker-registry-driver-fds'
__build__ = 0x000000

#__url__ = 'https://github.com/tobegit3hub/docker-registry-driver-fds'
__description__ = 'Docker registry driver fds'

setuptools.setup(
    name=__title__,
    version=__version__,
    author=__author__,
    author_email=__email__,
    maintainer=__maintainer__,
    maintainer_email=__email__,
    #url=__url__,
    description=__description__,
    #long_description=open('./readme.md').read(),
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 #'Programming Language :: Python :: 3.2',
                 #'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: Implementation :: CPython',
                 'Operating System :: OS Independent',
                 'Topic :: Utilities',
                 'License :: OSI Approved :: Apache Software License'],
    platforms=['Independent'],
    #license=open('./license').read(),
    namespace_packages=['docker_registry', 'docker_registry.drivers'],
    packages=['docker_registry', 'docker_registry.drivers'],
    package_data = {'docker_registry': ['../config/*']},
    #install_requires=open('./requirements.txt').read(),
    install_requires = ['docker-registry-core>=2,<3','galaxy-fds-sdk>=1.0.3'],
    zip_safe=True,
    #tests_require=open('./tests/requirements.txt').read(),
)
