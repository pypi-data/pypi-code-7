from setuptools import setup, find_packages
import subprocess
from srfp import __version__

setup(name='srfp',
    version=__version__,
    description='Client for the Simple Read-only File Protocol',
    author='Adam Brenecki',
    author_email='adam@brenecki.id.au',
    url='https://github.com/srfp-preservation/client',
    packages=find_packages(),
    include_package_data=True,
    setup_requires=[
        'setuptools_git>=0.3',
    ],
    install_requires=[
        'begins>=0.9,<0.9.99',
        'fs>=0.5.0,<0.5.99',
        'pyserial>=2.7,<2.7.99',
        'six>=1.8.0,'
    ],
    entry_points = {
        'console_scripts': [
            'srfpmnt = srfp.filesystem:start.start',
            'srfptree = srfp.demos.tree:main.start',
        ],
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Topic :: Communications :: File Sharing',
        'Topic :: System :: Archiving',
        'Topic :: System :: Filesystems',
    ]
)
