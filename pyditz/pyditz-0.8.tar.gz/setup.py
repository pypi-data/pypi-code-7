# Setup script for PyDitz.

# Bootstrap setuptools.
from conf.ez_setup import use_setuptools
use_setuptools()

from setuptools import setup

# Set the package version.
try:
    from hgtools.managers import MercurialManager
    version = MercurialManager().get_current_version(increment='0.1')
    with open("ditz/version.py", "w") as fp:
        fp.write("'%s'\n" % version)
except (RuntimeError, ImportError):
    pass

# Set up entry points.
from ditz.config import config

command = config.get('config', 'command')

entry_points = """
[console_scripts]
%(command)s = ditz.console:main
""" % globals()

# Do the setup.
import ditz
import ditz.pkginfo as info

setup(name             = info.__title__,
      author           = info.__author__,
      author_email     = info.__email__,
      description      = ditz.__doc__.strip(),
      long_description = "\n" + open("README").read(),
      license          = info.__license__,
      url              = info.__url__,
      classifiers      = info.__classifiers__.strip().split("\n"),

      packages = ["ditz"],
      include_package_data = True,
      use_vcs_version = {'increment': '0.1'},
      entry_points = entry_points,

      setup_requires = [
          'hgtools',
          'flake8',
      ],

      install_requires = [
          'pyyaml >= 3.10',
          'jinja2 >= 2.7',
          'six >= 1.8.0',
      ],

      tests_require = [
          'nose >= 1.3.0',
          'mock >= 1.0.1',
          'coverage >= 3.6',
      ],

      test_suite = 'nose.collector')

# flake8: noqa
