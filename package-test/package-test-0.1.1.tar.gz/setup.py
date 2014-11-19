#from distutils.core import setup

__version__ = '0.1.1'


DATA = dict(
    name = 'package-test',
    version = __version__,
    py_modules = ['drifter_functions'],
    description = 'that is a test ',
    long_description = '',
    license='no',
    author = 'huanxin',
    author_email = 'xhx509@gmail.com',
    url = '',
    keywords='test',

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
