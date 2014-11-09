# coding: utf-8
import sys
import os
from setuptools import setup, Extension
from functools import partial
import numpy as np

if sys.version_info < (3,2):
    print("At least Python 3.2 is required.")
    exit(1)


# load version info
exec(open("peanut/version.py").read())


USE_CYTHON = True   # command line option, try-import, ...


Extension = partial(Extension, extra_compile_args=["-O3"], include_dirs=[np.get_include()])


ext = '.pyx' if USE_CYTHON else '.c'
extensions = [
    Extension("peanut.{}".format(filename), ["peanut/{}{}".format(filename, ext)])
    for filename in "postprocessing input output alignment bitencoding rescue common".split()]


if USE_CYTHON:
    from Cython.Build import cythonize
    extensions = cythonize(extensions)


setup(
    name='peanut',
    version=__version__,
    author='Johannes Köster',
    author_email='johannes.koester@tu-dortmund.de',
    description='A massively parallel GPU read mapper using OpenCL.',
    license='MIT',
    url='http://peanut.readthedocs.org',
    packages=['peanut'],
    install_requires=["cython>=0.19", "numpy>=1.7", "pyopencl>=2013.1", "mako"],
    ext_modules=extensions,
    entry_points={"console_scripts": ["peanut = peanut:main"]},
    package_data={'': ['*.cl', '*.pyx', '*.pxd']},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
