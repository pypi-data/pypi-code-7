#from setuptools import setup   # Always prefer setuptools over distutils
#from distutils.core import setup

__version__ = '0.1.1'

DATA = dict(
    name='basemap_Jim',
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=__version__,

    description='basemap of Northwestern Atlantic Coastline for python plotting  .',
    

    # The project's main homepage.
    url='https://github.com/xhx509/drifter',
    #py_modules=['/basemap/basemap2'],
    # Author details
    author='Jammes Manning',
    author_email='james.manning@noaa.gov',

    # Choose your license
    license='update soon', #It is about copyright

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers

    scripts = ['basemap/basemap.py'],
    #py_modules=['basemap'],
    # What does your project relate to?
    keywords='basemap, python ,python plot',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['basemap'],
    classifiers = [
          'Programming Language :: Python',
          'Environment :: Other Environment',
          ],
    #package_dir = {'basemap':''},
    #package_dir={'basemap': '*.*'},

    # If there are data files included in your packages that need to be
    # installed in site-packages, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #include_package_data=True,
    #packages = find_packages(),
    # relative to the vfclust directory
    #package_data={
    #    'basemap':
    #         ['bostonharbor_coast.dat',
             
    #        ],
        
    #},
    install_requires = ['urlnorm>=1.1.2'],
    #install_requires=open('requirements.txt').read().split('\n'),
    long_description = ''
    #long_description = open('readme.md').read().split('\n'),

    #run custom code
)
SETUPTOOLS_DATA = dict(
  include_package_data = True,

)

try:
    import setuptools
    DATA.update(SETUPTOOLS_DATA)
    setuptools.setup(**DATA)
except ImportError:
    import distutils.core
    distutils.core.setup(**DATA)