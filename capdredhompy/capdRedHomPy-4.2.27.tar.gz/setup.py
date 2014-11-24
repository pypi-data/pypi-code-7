from setuptools import setup, Extension
#from distutils.core import setup
#from distutils.extension import Extension
import os, stat

# ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install  -e .

def remove_readonly(func, path, excinfo):
    os.chmod(os.path.dirname(path), stat.S_IRWXU)
    os.chmod(path, stat.S_IRWXU)
    func(path)

library_dirs = []

if 'CAPD_SRCDIR' in os.environ:
    import shutil

    for p in ['capdRedHom','tests']:
        if os.path.exists(p):
            shutil.rmtree(p, onerror=remove_readonly)

    for p in ['capdRedHom', 'tests']:
        if not os.path.exists(p):
            shutil.copytree(os.environ['CAPD_SRCDIR'] + '/python/' + p, p, shutil.ignore_patterns('*.pyc', '*~', '#*'))

    os.chmod('capdRedHom', 0755) # setup.py test needs to copy api.so there

    if os.path.exists('capdRedHom/version.py'):
        if os.access('capdRedHom/version.py', os.W_OK):
            shutil.copy('version.py', 'capdRedHom/version.py')
    elif os.access('capdRedHom', os.W_OK):
        shutil.copy('version.py', 'capdRedHom/version.py')


setup(name='capdRedHomPy',
      version='4.2.27',
      packages=[
          'capdRedHom',
          'capdRedHom.persistence',
      ],
      package_dir = {
          'capdRedHom' : 'capdRedHom',
          'capdRedHom.persistence' : 'capdRedHom/persistence',
      },
#      setup_requires=['nose>=1.0'],
      test_suite = 'nose.collector',
      )
