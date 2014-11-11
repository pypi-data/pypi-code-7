"""
PyStallone setup
"""
import sys
import os
from setuptools import setup

CLASSIFIERS = """\
Development Status :: 4 - Beta
Environment :: Console
Intended Audience :: Science/Research
License :: OSI Approved :: BSD License
Natural Language :: English
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Programming Language :: Java
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Topic :: Scientific/Engineering :: Bio-Informatics
Topic :: Scientific/Engineering :: Chemistry
Topic :: Scientific/Engineering :: Mathematics
Topic :: Scientific/Engineering :: Physics
Topic :: Software Development :: Libraries :: Java Libraries

"""


# support python 2 and 3
# TODO: recover code to handle python lists as array
jpype_species = 'JPype1>=0.5.6' if sys.version_info[0] == 2 else \
                'JPype1-py3>=0.5.5.2'

# java library
jar_name = 'stallone-1.0-SNAPSHOT-jar-with-dependencies.jar'

dest = os.path.abspath(os.path.join(os.getcwd(), 'pystallone', jar_name))


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


def download_library():
    import hashlib
    try:
        from urllib.request import urlopen
    except ImportError:
        from urllib2 import urlopen

    print("downloading current jar library to %s" % dest)
    # TODO: move destination of jar to maven central and validate via gpg
    base_url = 'http://www.mi.fu-berlin.de/users/marscher/'
    try:
        data = urlopen(base_url + jar_name).read()
        checksum = urlopen(
            base_url + jar_name + '.sha256').read().split(' ')[0]
        current = hashlib.sha256(data).hexdigest()
        if not current == checksum:
            raise RuntimeError('downloaded jar has invalid checksum.'
                               ' Is:\n"%s"\nShould be:\n"%s"' % (current, checksum))
        # write jar to pystallone/
        file = open(dest, 'w')
        file.write(str(data))
        print("finished")
    except IOError as ioe:
        print("error during download/saving jar:\n", ioe)
        sys.exit(1)
    except RuntimeError as re:
        print("error during validation:\n", re)
        sys.exit(2)
    except Exception as e:
        import traceback
        print("unknown exception occurred:\n")
        print(traceback.format_exc())
        sys.exit(3)


if not os.path.exists(dest):
    download_library()
    if not os.path.exists(dest):
        raise Exception("still not there - going to die... ^_^")


import versioneer
versioneer.VCS = 'git'
versioneer.versionfile_source = 'pystallone/_version.py'
versioneer.versionfile_build = None
versioneer.tag_prefix = 'v'  # tags are like v1.2.0
versioneer.parentdir_prefix = 'pystallone-'  # dirname like 'myproject-1.2.0'


metadata = dict(
    name='pystallone',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Python binding for Stallone java library',
    long_description=read('README.rst'),
    url='http://bitbucket.org/cmb-fu/stallone',
    author='Frank Noe, Martin K. Scherer',
    maintainer='Martin K. Scherer',
    author_email='stallone@lists.fu-berlin.de',
    packages=['pystallone'],
    package_data={'pystallone': [jar_name]},
    install_requires=[jpype_species,
                      'numpy >= 1.6.0'],
    tests_require=['unittest2', 'nose'],
    test_suite='nose.collector',
    zip_safe=False,
    keywords=['Markov modeling', 'Molecular trajectories analysis', 'MD'],
    license='Simplified BSD License',
    classifiers=[_f for _f in CLASSIFIERS.split('\n') if _f],
)

# do not install requirements on readthedocs
if os.environ.get('READTHEDOCS'):
    metadata['install_requires'] = []

setup(**metadata)
