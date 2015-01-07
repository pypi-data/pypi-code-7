"""pyjoint setup script"""

import imp
import os.path as pt
from setuptools import setup


def get_version():
    "Get version & version_info without importing pyjoint.__init__ "
    path = pt.join(pt.dirname(__file__), 'pyjoint', '__version__.py')
    mod = imp.load_source('pyjoint_version', path)
    return mod.VERSION, mod.VERSION_INFO

VERSION, VERSION_INFO = get_version()
DESCRIPTION = "Compute miter and tilt angles to create polyhedrons."
LONG_DESCRIPTION = open(pt.join(pt.dirname(__file__), 'README.rst')).read()
LONG_DESCRIPTION += open(pt.join(pt.dirname(__file__), 'HISTORY.rst')).read()
DEV_STATUS_MAP = {
    'alpha': '3 - Alpha',
    'beta': '4 - Beta',
    'rc': '4 - Beta',
    'final': '5 - Production/Stable'
}
if VERSION_INFO[3] == 'alpha' and VERSION_INFO[4] == 0:
    DEVSTATUS = '2 - Pre-Alpha'
else:
    DEVSTATUS = DEV_STATUS_MAP[VERSION_INFO[3]]


setup(
    name='pyjoint',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords='pyjoint miter tilt angles templates',
    author='Manuel Lopez',
    author_email='jmlopez.rod@gmail.com',
    url='http://pyjoint.readthedocs.org',
    license='BSD License',
    packages=[
        'pyjoint',
        'pyjoint.core',
    ],
    scripts=['bin/pyjoint'],
    install_requires=[
        'nose>=1.3',
    ],
    include_package_data=True,
    classifiers=[
        'Development Status :: %s' % DEVSTATUS,
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
