from setuptools import setup, Extension
import os, stat
#from distutils.extension import Extension
#from Cython.Distutils import build_ext
#from setuptools.command.build_ext import build_ext
import numpy

# ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install  -e .

def remove_readonly(func, path, excinfo):
    os.chmod(os.path.dirname(path), stat.S_IRWXU)
    os.chmod(path, stat.S_IRWXU)
    func(path)

library_dirs = []

if 'CAPD_SRCDIR' in os.environ:
    import shutil

    for p in ['capdRedHom','tests', 'src']:
        if os.path.exists(p):
            shutil.rmtree(p, onerror=remove_readonly)

    for p in ['capdRedHom', 'tests', 'src']:
        if not os.path.exists(p):
            shutil.copytree(os.environ['CAPD_SRCDIR'] + '/python/' + p, p, shutil.ignore_patterns('*.pyc', '*~', '#*'))
            os.chmod(p, 0755) # for generated files



    if os.path.exists('capdRedHom/version.py'):
        if os.access('capdRedHom/version.py', os.W_OK):
            shutil.copy('version.py', 'capdRedHom/version.py')
    elif os.access('capdRedHom', os.W_OK):
        shutil.copy('version.py', 'capdRedHom/version.py')




setup(name='capdRedHomPy',
      version='4.2.32',
      packages=[
          'capdRedHom',
          'capdRedHom.persistence',
      ],
      package_dir = {
          'capdRedHom' : 'capdRedHom',
          'capdRedHom.persistence' : 'capdRedHom/persistence',
      },
#      setup_requires=['nose>=1.0'],
      install_requires=['cython'],
      test_suite = 'nose.collector',
#      cmdclass = {'build_ext': build_ext},
      ext_modules = [Extension("capdRedHom.numpy_helpers",
                               sources=["src/numpy_helpers.c"],
                               include_dirs=[numpy.get_include()])],
      )
