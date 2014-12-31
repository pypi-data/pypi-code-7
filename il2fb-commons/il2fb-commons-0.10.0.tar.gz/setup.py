# -*- coding: utf-8 -*-

import os

from setuptools import setup


__here__ = os.path.abspath(os.path.dirname(__file__))

README = open(os.path.join(__here__, 'README.rst')).read()
REQUIREMENTS = [
    i.strip()
    for i in open(os.path.join(__here__, 'requirements.txt')).readlines()
]

# Get VERSION
version_file = os.path.join('il2fb', 'commons', 'version.py')
# Use exec for compabibility with Python 3
exec(open(version_file).read())

setup(
    name='il2fb-commons',
    version=VERSION,
    description="Common helpers and data structures for projects related to "
                "IL-2 Forgotten Battles",
    long_description=README,
    keywords=[
        'il2', 'il-2', 'fb', 'forgotten battles', 'common', 'structure',
    ],
    license='LGPLv3',
    url='https://github.com/IL2HorusTeam/il2fb-commons',
    author='Alexander Oblovatniy',
    author_email='oblovatniy@gmail.com',
    packages=[
        'il2fb.commons',
    ],
    namespace_packages=[
        'il2fb',
    ],
    include_package_data=True,
    install_requires=REQUIREMENTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries',
    ],
    platforms=[
        'any',
    ],
)
