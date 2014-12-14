from setuptools import setup, Extension, Command
from setuptools.command.sdist import sdist
from setuptools.command.build_ext import build_ext


# my commands
def generate_modules():
    from Cython.Build import cythonize
    cythonize('pyfde/*.pyx')


class my_sdist(sdist):

    def run(self):
        generate_modules()
        sdist.run(self)


class my_build_ext(build_ext):

    def run(self):
        import os.path
        if not os.path.isfile('pyfde/classicde.c'):
            generate_modules()

        build_ext.run(self)


class my_clean(Command):

    description = "Removes the generated files from the directory"
    user_options = []

    def initialize_options(self):
        pass

    def run(self):
        import os
        import glob
        import shutil

        patterns = ['pyfde/*.c', 'pyfde/*.so', 'pyfde/*.html', 'MANIFEST']
        dirs = ['pyfde/__pycache__', 'tests/__pycache__', 'PyFDE.egg-info',
                'build', 'dist']

        for pat in patterns:
            for junk in glob.iglob(pat):
                os.remove(junk)

        for dir_ in dirs:
            shutil.rmtree(dir_, ignore_errors=True)

    def finalize_options(self):
        pass

# information for the setup
with open('README.rst') as readme:
    long_description = readme.read()

import numpy

setup(
    name='PyFDE',
    version='1.2.0',
    description='A fast differential evolution module',
    author='Lucas Hermann Negri',
    author_email='lucashnegri@gmail.com',
    url='https://bitbucket.org/lucashnegri/pyfde',
    packages=['pyfde'],
    install_requires=['numpy'],
    ext_modules=[
        Extension('pyfde.classicde', ['pyfde/classicde.c']),
        Extension('pyfde.jade', ['pyfde/jade.c']),
        Extension('pyfde.rng', ['pyfde/rng.c']),
        Extension('pyfde.bench', ['pyfde/bench.c'])
    ],
    cmdclass={
        'build_ext': my_build_ext,
        'clean': my_clean,
        'sdist': my_sdist,
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence'
    ],
    license='MIT',
    include_dirs=[numpy.get_include()],
    test_suite='tests',
    keywords='differential evolution search optimization evolutionary'
)
