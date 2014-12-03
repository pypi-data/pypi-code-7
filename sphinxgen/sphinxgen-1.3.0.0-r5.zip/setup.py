import ez_setup
ez_setup.use_setuptools()


from setuptools import setup, find_packages
import sys

sys.path.insert(0, '.')
import sphinxgen
import sphinxgen.version as proj_version


setup(
    name='sphinxgen',
    author='Brian Mearns',
    author_email='bmearns@ieee.org',
    url='https://bitbucket.org/bmearns/sphinxgen',
    license='GPLv3+ --- See LICENSE.txt',

    #Provide a brief description. The long description is loaded from README.rst
    #description='Brief description of the package.',

    #Load the version string from the built-in version module.
    version=proj_version.setuptools_string(),

    #Uses MANIFEST.in to decide what to put in source distribution.
    include_package_data = True,
    
    #Automaticaly search for modules, identified by __init__.py
    packages = find_packages('.', exclude=["tests"]),

    #Other pypi packages that are dependencies for this package.
    # To specify a particular version, do like 'package (>=1.2.3)'
    requires = ['jinja2'],

    #pypi packages that aren't necessarily required by the package, but are
    # required for certain setup.py commands. These will not be installed, but will
    # be downloaded into the local directory when setup.py is runn.
    setup_requires = [
        'nose>=1.0',
        'sphinx>=0.5',
        'sphinx_rtd_theme',
        'nosetp',
        'sphinxcontrib-autoprogram',
    ],

    cmdclass = {
        'sphinxgen': sphinxgen.sphinxgen,
    },

    entry_points = {
        'console_scripts': [
            'sphinxgen=sphinxgen:main',
        ],
        'distutils.commands': [
            'sphinxgen=sphinxgen:sphinxgen',
        ],
    },

    #Less desirable than the nosetests command, but allows you to use the
    # standard `tests` command to run nosetests.
    test_suite = 'nose.collector',
    tests_require = ['nose>=1.0', 'pychangelog>=1.1'],

    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],
)
